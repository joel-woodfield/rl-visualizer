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
  const [cellPos, setCellPos] = useState<{ x: number; y: number } | null>(null);
  const [canvasWidth, setCanvasWidth] = useState<number>(300);
  const [canvasHeight, setCanvasHeight] = useState<number>(300);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const gridSpacing = 2;

  const getFeatureCells = (array: number[][][], x: number, y: number): number[] => {
    const panelHeight = array[0].length;
    const panelWidth = array[0][0].length;
    const cellX = Math.floor(x * panelWidth);
    const cellY = Math.floor(y * panelHeight);
    setCellPos({ x: cellX, y: cellY });
    return array.map(panel => panel[cellY][cellX]);
  };

  const drawFeatures = (cells: number[], canvas: HTMLCanvasElement | null) => {
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const numCells = cells.length;
    let numCellsAcross = Math.floor(Math.sqrt(numCells));
    let numCellsDown = Math.ceil(numCells / numCellsAcross);
    while (numCellsAcross * numCellsDown < numCells) {
      ++numCellsAcross;
      numCellsDown = Math.ceil(numCells / numCellsAcross);
    }

    const cellWidth = Math.floor((canvasWidth - (numCellsAcross - 1) * gridSpacing) / numCellsAcross);
    const cellHeight = Math.floor((canvasHeight - (numCellsDown - 1) * gridSpacing) / numCellsDown);
    const cellSize = Math.min(cellWidth, cellHeight);

    canvas.width = canvasWidth;
    canvas.height = canvasHeight;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (let i = 0; i < numCellsDown; ++i) {
      for (let j = 0; j < numCellsAcross; ++j) {
        const idx = i * numCellsAcross + j;
        if (idx >= numCells) break;
        const value = cells[idx];
        ctx.fillStyle = `rgb(${value}, ${value}, ${value})`;
        ctx.fillRect(
          j * (cellSize + gridSpacing),
          i * (cellSize + gridSpacing),
          cellSize,
          cellSize
        );
      }
    }
  };

  useEffect(() => {
    if (!position || !selectedAttr || !canvasRef.current || !gridData[selectedAttr]) return;
    const cells = getFeatureCells(gridData[selectedAttr]!, position.x, position.y);
    drawFeatures(cells, canvasRef.current);
  }, [selectedAttr, position, gridData]);

  if (!position || !container) return null;

  const content = (
    <div>
      <h3>Feature Viewer</h3>
      <p>Clicked position: ({position.x.toFixed(2)}, {position.y.toFixed(2)})</p>
      <p>
        Clicked cell position: {cellPos ? `(${cellPos.x}, ${cellPos.y})` : "Unknown"}
      </p>
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
      <div style={{ marginTop: "16px" }}>
        <canvas ref={canvasRef} style={{ border: "1px solid #ccc" }} />
      </div>
      <button style={{ marginTop: "24px" }} onClick={onClose}>
        Close
      </button>
    </div>
  );

  return ReactDOM.createPortal(content, container);
};

export default FeatureViewer;

