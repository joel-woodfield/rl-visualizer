import React, { useEffect, useRef, useState } from "react";
import ReactDOM from "react-dom";

export type FeatureViewerProps = {
  position: { x: number; y: number } | null;
  gridData: Record<string, number[][][] | null>;
  container: HTMLElement | null;
  onClose: () => void;
};

const FeatureViewer: React.FC<FeatureViewerProps> = ({
  position,
  gridData,
  container,
  onClose,
}) => {
  const [selectedAttr, setSelectedAttr] = useState<string | null>(null);

  if (!position) {
    console.log("null pos");
    return null;
  }
  if (!container) {
     console.log("null container");
     return null;
  }

  const content = (
    <div>
      <h3>Feature Viewer</h3>
      <p>Clicked position: ({position.x.toFixed(2)}, {position.y.toFixed(2)})</p>
      <label>
        Select Grid Attribute:
        <select
          value={selectedAttr ?? ""}
          onChange={(e) => setSelectedAttr(e.target.value)}
        >
          <option value="" disabled>
            -- Choose an attribute --
          </option>
          {Object.entries(gridData).map(([attr, grid]) =>
            grid ? (
              <option key={attr} value={attr}>
                {attr}
              </option>
            ) : null
          )}
        </select>
      </label>
      <div style={{ marginTop: "16px" }}>Grid display will go here...</div>
      <button style={{ marginTop: "24px" }} onClick={onClose}>
        Close
      </button>
    </div>
  );

  return ReactDOM.createPortal(content, container);
};

export default FeatureViewer;

