import "./index.css";
import FileUpload from "./FileUpload";
import ImageViewer from "./ImageViewer";
import GridViewer from "./GridViewer";
import TextViewer from "./TextViewer";
import Sidebar from "./Sidebar";
import TimestepSlider from "./TimestepSlider";
import { useState, useRef, useEffect } from "react";

const App = () => {
  const [fileUploaded, setFileUploaded] = useState(false);

  const [data, setData] = useState<Record<string, null | string | string[] | number[][][]>>({});
  const [imageData, setImageData] = useState<Record<string, string | null>>({});
  const [gridData, setGridData] = useState<Record<string, number[][][] | null>>({});
  const [textData, setTextData] = useState<Record<string, string | string[] | null>>({});

  const [selectedTextAttributes, setSelectedTextAttributes] = useState<string[]>([]);
  const [selectedColorAttributes, setSelectedColorAttributes] = useState<string[]>([]);
  const [selectedGridAttributes, setSelectedGridAttributes] = useState<string[]>([]);
  const [timestep, setTimestep] = useState<number>(0);
  const gridContainerRef = useRef<HTMLDivElement | null>(null);

  const handleFileUpload = () => {
    setFileUploaded(true);
  };

  // fetch the data on init or if timestep changes
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`/data?timestep=${timestep}`);
        if (!response.ok) throw new Error("Failed to fetch data");

        const data = await response.json();
        setData(data.data);
      } catch (error) {
        console.log("Error fetching data:", error);
      }
    }

    fetchData();
  }, [timestep, fileUploaded]);

  useEffect(() => {
    const colorData: Record<string, string | null> = {};
    selectedColorAttributes.forEach(attr => {
      if (attr in data && typeof data[attr] === "string") {
        colorData[attr] = `data:image/png;base64,${data[attr]}`;
      }
    });
    setImageData(colorData);
  }, [data, selectedColorAttributes]);

  useEffect(() => {
    const gridData: Record<string, number[][][] | null> = {};
    selectedGridAttributes.forEach(attr => {
      const attrData = attr in data? data[attr] : null;
      if (
        attrData !== null &&
        Array.isArray(attrData) &&
        Array.isArray(attrData[0]) &&
        Array.isArray(attrData[0][0]) &&
        typeof attrData[0][0][0] === "number"
      ) {
        gridData[attr] = attrData as number[][][];
      }
    });
    setGridData(gridData);
  }, [data, selectedGridAttributes]);

  useEffect(() => {
    const textData: Record<string, string | string[] | null> = {};
    selectedTextAttributes.forEach(attr => {
      if (attr in data) {
        textData[attr] = data[attr] as string[] | string[];
      }
    });
    setTextData(textData);
  }, [data, selectedTextAttributes]);

  return (
      <div className="app-container">
        {!fileUploaded ? (
            <div className="file-upload-container">
              <FileUpload onUpload={handleFileUpload} />
            </div>
        ) : (
            <>
              <div className="image-area">
                <ImageViewer data={imageData} />
              </div>

              <div ref={gridContainerRef} className="grid-area">
                <GridViewer data={gridData} containerRef={gridContainerRef} />
              </div>

              <div className="text-area">
                <TextViewer data={textData} />
              </div>

              <div className="sidebar">
                <Sidebar
                    selectedTextAttributes={selectedTextAttributes}
                    setSelectedTextAttributes={setSelectedTextAttributes}
                    selectedColorAttributes={selectedColorAttributes}
                    setSelectedColorAttributes={setSelectedColorAttributes}
                    selectedGridAttributes={selectedGridAttributes}
                    setSelectedGridAttributes={setSelectedGridAttributes}
                />
              </div>

              <div className="timestep-slider">
                <TimestepSlider timestep={timestep} setTimestep={setTimestep} />
              </div>
            </>
        )}
      </div>
  );
};

export default App;
