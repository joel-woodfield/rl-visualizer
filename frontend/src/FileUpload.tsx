import { useState } from "react";

interface FileUploadProps {
  onUpload: () => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onUpload }) => {
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState<string>("");

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setFile(event.target.files[0]);
      setMessage(""); // Reset message on new selection
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("/upload_file", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        setMessage("File uploaded successfully!");
        onUpload(); // Notify parent (App.tsx) that file is uploaded
      } else {
        setMessage("File upload failed.");
      }
    } catch (error) {
      setMessage("Error uploading file.");
    }
  };

  return (
    <div style={{ padding: "20px", textAlign: "center" }}>
      <h2>Upload an HDF5 File</h2>
      <input type="file" accept=".h5" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={!file} style={{ marginLeft: "10px" }}>
        Upload
      </button>
      {message && <p>{message}</p>}
    </div>
  );
};

export default FileUpload;

