import { useState, useEffect } from "react";

interface TextViewerProps {
  data: Record<string, string | string[] | null>;
}

const TextViewer: React.FC<TextViewerProps> = ({ data }) => {
  return (
    <div style={{ padding: "10px" }}>
      <h3>Text Attributes</h3>
      {!data || Object.keys(data).length === 0 ? (
        <p>No text attributes selected</p>
      ) : (
        <ul style={{ listStyleType: "none", padding: 0, margin: 0 }}>
          {Object.entries(data).map(([attr, value]) => (
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

