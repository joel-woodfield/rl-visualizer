
import base64
import os
import h5py
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import numpy as np

app = FastAPI()

# Store the loaded HDF5 file in memory
h5_file = None
h5_file_path = None

# Define where uploaded files are temporarily stored
UPLOAD_DIR = "/tmp"  # Adjust this if needed

# Serve frontend (React build)
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR, html=True), name="frontend")

@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")

@app.post("/upload_file")
async def upload_file(file: UploadFile = File(...)):
    """Uploads an HDF5 file and loads it into memory."""
    global h5_file, h5_file_path

    # Ensure the upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Save the file to a temporary location
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())

    # Close previous file if one was open
    if h5_file:
        h5_file.close()

    # Open the new HDF5 file
    h5_file_path = file_location
    h5_file = h5py.File(h5_file_path, "r")

    return {"message": "File uploaded and loaded successfully", "file_path": h5_file_path}

@app.get("/attributes")
async def get_attributes():
    """Returns available attributes in the loaded HDF5 file."""
    if h5_file is None:
        raise HTTPException(status_code=400, detail="No file loaded.")
    
    return {"attributes": list(h5_file.keys())}

@app.get("/dtypes")
async def get_dtypes():
    """Returns the attribute types stored in _dtypes."""
    if h5_file is None:
        raise HTTPException(status_code=400, detail="No file loaded.")

    if "_dtypes" not in h5_file:
        raise HTTPException(status_code=400, detail="No _dtypes group found.")

    dtype_metadata = h5_file["_dtypes"].attrs
    dtypes = {
        attr: dtype_metadata[attr]
        for attr in dtype_metadata.keys()
        if not attr.startswith("_")  # Ignore attributes starting with "_"
    }

    return {"dtypes": dtypes}

@app.get("/data")
async def get_data(timestep: int):
    """Returns attribute values for a given timestep."""
    if h5_file is None:
        raise HTTPException(status_code=400, detail="No file loaded.")

    data = {}
    dtype_metadata = h5_file["_dtypes"].attrs  # Retrieve stored types

    for attr in h5_file.keys():
        if attr == "_dtypes":
            continue  # Skip metadata group

        dataset = h5_file[attr]
        rlviz_type = dtype_metadata.get(attr, "unknown")  # Retrieve stored type

        value = dataset[timestep]

        # Use stored type to determine how to process data
        if rlviz_type == "RlvizType.TEXT":
            if isinstance(value, bytes):
                value = value.decode("utf-8")
            elif isinstance(value, np.ndarray) and dataset.dtype.kind == "O":
                value = [v.decode("utf-8") if isinstance(v, bytes) else v for v in value]
        
        # Convert COLOR attributes (images) to Base64
        elif rlviz_type == "RlvizType.COLOR" and isinstance(value, np.ndarray):
            try:
                import io
                from PIL import Image

                img = Image.fromarray(value.astype(np.uint8))  # Ensure image is uint8
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                value = base64.b64encode(buffered.getvalue()).decode("utf-8")

            except Exception as e:
                print(f"Error converting image {attr}: {e}")
                value = None

        elif isinstance(value, np.ndarray):
            value = value.tolist()  # Convert NumPy array to JSON

        data[attr] = value

    return {"timestep": timestep, "data": data}

@app.get("/num_timesteps")
async def get_num_timesteps():
    """Returns the number of timesteps in the HDF5 file."""
    if h5_file is None:
        raise HTTPException(status_code=400, detail="No file loaded.")

    # Assuming timesteps are determined by the first dataset's length
    first_attr = next(iter(h5_file.keys()), None)
    if first_attr is None:
        raise HTTPException(status_code=400, detail="No attributes found in HDF5 file.")

    num_timesteps = len(h5_file[first_attr])
    return {"num_timesteps": num_timesteps}



def start_server(host="127.0.0.1", port=8000):
    """Starts the FastAPI server."""
    import uvicorn
    uvicorn.run(app, host=host, port=port)

