import { useState, useEffect } from "react";

interface TimestepSliderProps {
  timestep: number;
  setTimestep: React.Dispatch<React.SetStateAction<number>>;
}


const TimestepSlider: React.FC<TimestepSliderProps> = ({ timestep, setTimestep }) => {
  const [numTimesteps, setNumTimesteps] = useState<number>(100); // Default to 100

  useEffect(() => {
    const fetchNumTimesteps = async () => {
      try {
        const response = await fetch("/num_timesteps");
        if (!response.ok) throw new Error("Failed to fetch number of timesteps");

        const data = await response.json();
        setNumTimesteps(data.num_timesteps);
      } catch (error) {
        console.error("Error fetching number of timesteps:", error);
      }
    };

    fetchNumTimesteps();
  }, []);

  // Handle left/right arrow key events
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      event.preventDefault(); // Stops default arrow key behavior (like scrolling)
  
      setTimestep((prevTimestep) => {
        if (event.key === "ArrowLeft") {
          return Math.max(0, prevTimestep - 1);
        } else if (event.key === "ArrowRight") {
          return Math.min(numTimesteps - 1, prevTimestep + 1);
        }
        return prevTimestep;
      });
    };
  
    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [numTimesteps]);


  return (
    <div style={{ padding: "10px", width: "100%" }}>
      <input
        type="range"
        min="0"
        max={numTimesteps - 1}
        value={timestep}
        onChange={(e) => setTimestep(Number(e.target.value))}
        style={{
          width: "100%",
          height: "8px",
          margin: "0 auto",
          display: "block"
        }}
      />
      <p style={{ textAlign: "center" }}>
        Timestep: {timestep} / {numTimesteps - 1} (Use ← / → to change)
      </p>
    </div>
  );
};

export default TimestepSlider;

