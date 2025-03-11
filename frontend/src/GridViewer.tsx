import { useState, useEffect, useRef } from "react";

interface GridViewerProps {
    selectedAttributes: string[];
    timestep: number;
    containerRef: React.RefObject<HTMLDivElement | null>;
    gridSpacing?: number;
}

interface Panel {
    data: number[][]
}

interface Grid {
    panels: Panel[];
    width: number;
    height: number;
}

const GridViewer: React.FC<GridViewerProps> = ({
                                                   selectedAttributes,
                                                   timestep,
                                                   containerRef,
                                                   gridSpacing = 10,
                                               }) => {
    const [gridData, setGridData] = useState<Record<string, number[][][] | null>>({});
    const [canvasSize, setCanvasSize] = useState<number>(300);
    const canvasRefs = useRef<Record<string, HTMLCanvasElement | null>>({});

    useEffect(() => {
        const fetchData = async () => {
            if (selectedAttributes.length === 0) {
                setGridData({});
                return;
            }

            try {
                const response = await fetch(`/data?timestep=${timestep}`);
                if (!response.ok) throw new Error("Failed to fetch data");

                const data = await response.json();

                const filteredData: Record<string, number[][][]> = {};
                selectedAttributes.forEach(attr => {
                    if (attr in data.data && Array.isArray(data.data[attr])) {
                        filteredData[attr] = data.data[attr]; // Expecting (d, s, s) format
                    }
                });

                setGridData(filteredData);
            } catch (error) {
                console.error("Error fetching grid data:", error);
            }
        };

        fetchData();
    }, [timestep, selectedAttributes]);

    useEffect(() => {
        drawGrids();
    }, [gridData, gridSpacing, canvasSize]);

    useEffect(() => {
        const updateCanvasSize = () => {
            if (!containerRef.current) return;

            // Get the actual content size inside `.grid-area`
            const { width, height } = containerRef.current.getBoundingClientRect();

            // Subtract padding (16px on left & right)
            const effectiveWidth = width - 32;
            const effectiveHeight = height - 32;

            // Ensure the canvas fits within the adjusted area
            setCanvasSize(Math.min(effectiveWidth, effectiveHeight));
        };

        updateCanvasSize(); // Run once on mount

        // Observe changes in container size
        const resizeObserver = new ResizeObserver(updateCanvasSize);
        if (containerRef.current) {
            resizeObserver.observe(containerRef.current);
        }

        return () => resizeObserver.disconnect();
    }, []);


    const convertToGrid = (array: number[][][]): Grid => {
        const numPanels = array.length;

        let gridWidth = Math.floor(Math.sqrt(numPanels));
        let gridHeight = Math.ceil(numPanels /  gridWidth);
        while (gridWidth * gridHeight < numPanels) {
            ++gridWidth;
            gridHeight = Math.ceil(numPanels / gridWidth);
        }

        const panels: Panel[] = array.map(data => ({
            data,
        }));

        return {
            panels,
            width: gridWidth,
            height: gridHeight,
        };
    };

    const drawGrid = (grid: Grid, canvas: HTMLCanvasElement | null) => {
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        // Compute canvas size
        const panelWidth = Math.floor((canvasSize - (grid.width - 1) * gridSpacing) / grid.width);
        const panelHeight = Math.floor((canvasSize - (grid.height - 1) * gridSpacing) / grid.height);

        // Set canvas size
        canvas.width = canvasSize;
        canvas.height = canvasSize;
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Draw each panel at its correct position
        grid.panels.forEach((panel, index) => {
            const col = index % grid.width;
            const row = Math.floor(index / grid.width);
            const x = col * (panelWidth + gridSpacing);
            const y = row * (panelHeight + gridSpacing);

            drawPanel(ctx, panel, x, y, panelWidth, panelHeight);
        });
    };

    const drawPanel = (ctx: CanvasRenderingContext2D, panel: Panel, x: number, y: number, width: number, height: number) => {
        const { data } = panel;
        const c = data.length; // c x c grid size
        const cellSize = width / c; // Compute cell size dynamically

        for (let i = 0; i < c; i++) {
            for (let j = 0; j < c; j++) {
                const value = data[i][j]; // Grayscale value (0-255)
                ctx.fillStyle = `rgb(${value}, ${value}, ${value})`;
                ctx.fillRect(
                    Math.floor(x + j * cellSize),
                    Math.floor(y + i * cellSize),
                    Math.ceil(cellSize),
                    Math.ceil(cellSize)
                );
            }
        }
    };

    const drawGrids = () => {
        Object.entries(gridData).forEach(([attr, array]) => {
            if (!array) return;
            let grid = convertToGrid(array);
            drawGrid(grid, canvasRefs.current[attr]);
        });
    };

    return (
        <div style={{ padding: "10px", textAlign: "center", display: "flex", flexDirection: "column", gap: "10px" }}>
            {selectedAttributes.length === 0 ? (
                <p>No grids selected</p>
            ) : (
                Object.keys(gridData).map(attr => (
                    <div key={attr} style={{ width: canvasSize, height: canvasSize }}>
                        <h4 style={{ margin: "4px 0", fontSize: "16px", color: "#444" }}>{attr}</h4>
                        <canvas ref={el => { canvasRefs.current[attr] = el; }} width={canvasSize} height={canvasSize} />
                    </div>
                ))
            )}
        </div>
    );
};

export default GridViewer;
