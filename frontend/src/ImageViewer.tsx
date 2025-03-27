import { useState, useEffect } from "react";

interface ImageViewerProps {
  data: Record<string, string | null>;
}

const ImageViewer: React.FC<ImageViewerProps> = ({ data }) => {
  return (
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
                // onClick={(e) => handleClick(e, attr)}
              />
            ) : (
              <p>Invalid Image</p>
            )}
          </div>
        ))
      )}
    </div>
  );
};

export default ImageViewer;

