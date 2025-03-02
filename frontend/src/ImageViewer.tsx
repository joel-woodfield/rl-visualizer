import { useState, useEffect } from "react";

interface ImageViewerProps {
  selectedAttributes: string[]; // Only COLOR attributes
  timestep: number; // Current timestep
}

const ImageViewer: React.FC<ImageViewerProps> = ({ selectedAttributes, timestep }) => {
  const [imageData, setImageData] = useState<Record<string, string | null>>({});

  useEffect(() => {
    const fetchData = async () => {
      if (selectedAttributes.length === 0) {
        setImageData({}); // Clear images if nothing is selected
        return;
      }

      try {
        const response = await fetch(`/data?timestep=${timestep}`);
        if (!response.ok) throw new Error("Failed to fetch data");

        const data = await response.json();

        // Extract only selected COLOR attributes
        const filteredData: Record<string, string | null> = {};
        selectedAttributes.forEach(attr => {
          if (attr in data.data && typeof data.data[attr] === "string") {
            filteredData[attr] = `data:image/png;base64,${data.data[attr]}`;
          }
        });

        setImageData(filteredData);
      } catch (error) {
        console.error("Error fetching image data:", error);
      }
    };

    fetchData();
  }, [timestep, selectedAttributes]);

  return (
    <div style={{ padding: "10px", height: "100%", display: "flex", alignItems: "center", justifyContent: "center" }}>
      {selectedAttributes.length === 0 ? (
        <p>No images selected</p>
      ) : (
        Object.entries(imageData).map(([attr, src]) => (
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
                  height: "100%", 
                  objectFit: "contain" // Ensures full coverage while keeping proportions
                }}
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

