import { useState, useEffect } from "react";

interface TextViewerProps {
  selectedAttributes: string[]; // Only TEXT attributes
  timestep: number; // Current timestep
}

const TextViewer: React.FC<TextViewerProps> = ({ selectedAttributes, timestep }) => {
  const [textData, setTextData] = useState<Record<string, string | string[]>>({});

  useEffect(() => {
    const fetchData = async () => {
      if (selectedAttributes.length === 0) {
        setTextData({});
        return;
      }

      try {
        const response = await fetch(`/data?timestep=${timestep}`);
        if (!response.ok) throw new Error("Failed to fetch data");

        const data = await response.json();

        // Filter only the selected TEXT attributes
        const filteredData: Record<string, string | string[]> = {};
        selectedAttributes.forEach(attr => {
          if (attr in data.data) {
            filteredData[attr] = data.data[attr];
          }
        });

        setTextData(filteredData);
      } catch (error) {
        console.error("Error fetching text data:", error);
      }
    };

    fetchData();
  }, [timestep, selectedAttributes]);

  return (
    <div style={{ padding: "10px" }}>
      <h3>Text Attributes</h3>
      {!textData || Object.keys(textData).length === 0 ? (
        <p>No text attributes selected</p>
      ) : (
        <ul style={{ listStyleType: "none", padding: 0, margin: 0 }}>
          {Object.entries(textData).map(([attr, value]) => (
            <li key={attr}>
              <strong>{attr}:</strong> {Array.isArray(value) ? value.join(", ") : value}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default TextViewer;

