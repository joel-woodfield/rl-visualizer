import "./index.css";
import FileUpload from "./FileUpload";
import ImageViewer from "./ImageViewer";
import GridViewer from "./GridViewer";
import TextViewer from "./TextViewer";
import Sidebar from "./Sidebar";
import TimestepSlider from "./TimestepSlider";
import { useState, useRef } from "react";

const App = () => {
  const [fileUploaded, setFileUploaded] = useState(false);
  const [selectedTextAttributes, setSelectedTextAttributes] = useState<string[]>([]);
  const [selectedColorAttributes, setSelectedColorAttributes] = useState<string[]>([]);
  const [selectedGridAttributes, setSelectedGridAttributes] = useState<string[]>([]);
  const [timestep, setTimestep] = useState<number>(0);
  const gridContainerRef = useRef<HTMLDivElement | null>(null);

  const handleFileUpload = () => {
    setFileUploaded(true);
  };

  return (
      <div className="app-container">
        {!fileUploaded ? (
            <div className="file-upload-container">
              <FileUpload onUpload={handleFileUpload} />
            </div>
        ) : (
            <>
              <div className="image-area">
                <ImageViewer selectedAttributes={selectedColorAttributes} timestep={timestep} />
              </div>

              <div ref={gridContainerRef} className="grid-area">
                <GridViewer
                  selectedAttributes={selectedGridAttributes}
                  timestep={timestep}
                  containerRef={gridContainerRef}
                />
              </div>

              <div className="text-area">
                <TextViewer selectedAttributes={selectedTextAttributes} timestep={timestep} />
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
