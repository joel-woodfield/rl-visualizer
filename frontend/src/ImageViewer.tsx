import FeatureViewer from "./FeatureViewer";
import { useState, useEffect, useRef } from "react";

interface ImageViewerProps {
  data: Record<string, string | null>;
  gridData: Record<string, number[][][] | null>;
}

const ImageViewer: React.FC<ImageViewerProps> = ({ data, gridData }) => {
  const [clickPos, setClickPos] = useState<{ x: number; y: number } | null>(null);
  const [popupContainer, setPopupContainer] = useState<HTMLElement | null>(null);
  const popupRef = useRef<Window | null>(null);

  const handleClick = (e: React.MouseEvent<HTMLImageElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width;
    const y = (e.clientY - rect.top) / rect.height;
    console.log(`clicked (${x},${y})`);
    setClickPos({ x, y });

    const popup = window.open("", "_blank", "width=600,height=400");
    if (!popup) {
      alert("Popup blocked!");
      return;
    }

    popup.document.write(`
      <html>
        <head><title>Feature Viewer</title></head>
        <body><div id="feature-root"></div></body>
      </html>
    `);
    popup.document.close();
    popupRef.current = popup;
  
    // Poll for container instead of using popup.onload
    const checkReady = setInterval(() => {
      const container = popup.document.getElementById("feature-root");
      if (container) {
        clearInterval(checkReady);
        setPopupContainer(container);
      }
    }, 10);
  };

  return (
    <>
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", width: "100%", height: "100%", padding: "10px" }}>
        {Object.keys(data).length === 0 ? (
          <p>No images selected</p>
        ) : (
          Object.entries(data).map(([attr, src]) => (
            <div key={attr} style={{ width: "100%", height: "100%" }}>
              <h4 style={{ margin: "4px 0", fontSize: "16px", color: "#444" }}>
                {attr}
              </h4>
              {src ? (
                <img
                  src={src}
                  alt={attr}
                  style={{
                    width: "100%", 
                    height: "auto", 
                    objectFit: "contain" // Ensures full coverage while keeping proportions
                  }}
                  onClick={handleClick}
                />
              ) : (
                <p>Invalid Image</p>
              )}
            </div>
          ))
        )}
      </div>
     {popupContainer && clickPos && (
        <FeatureViewer
          container={popupContainer}
          position={clickPos}
          gridData={gridData}
          onClose={() => {
            popupRef.current?.close();
            setPopupContainer(null);
            setClickPos(null);
          }}
        />
      )}
    </>
  );
 };

export default ImageViewer;

