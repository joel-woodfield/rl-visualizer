import { useState, useEffect } from "react";

interface SidebarProps {
  selectedTextAttributes: string[];
  setSelectedTextAttributes: React.Dispatch<React.SetStateAction<string[]>>;
  selectedColorAttributes: string[];
  setSelectedColorAttributes: React.Dispatch<React.SetStateAction<string[]>>;
  selectedGridAttributes: string[];
  setSelectedGridAttributes: React.Dispatch<React.SetStateAction<string[]>>;
}


const Sidebar: React.FC<SidebarProps> = ({
  selectedTextAttributes,
  setSelectedTextAttributes,
  selectedColorAttributes,
  setSelectedColorAttributes,
  selectedGridAttributes,
  setSelectedGridAttributes,
}) => {
  const [colorAttributes, setColorAttributes] = useState<string[]>([]);
  const [textAttributes, setTextAttributes] = useState<string[]>([]);
  const [gridAttributes, setGridAttributes] = useState<string[]>([]);

  useEffect(() => {
    const fetchAttributes = async () => {
      try {
        // Fetch attributes from backend
        const attrResponse = await fetch("/attributes");
        if (!attrResponse.ok) throw new Error("Failed to fetch attributes");

        const attrData = await attrResponse.json();
        let attributes: string[] = attrData.attributes.filter((attr: string) => !attr.startsWith("_"));

        // Fetch dtypes from backend
        const dtypeResponse = await fetch("/dtypes");
        if (!dtypeResponse.ok) throw new Error("Failed to fetch dtypes");

        const dtypeData = await dtypeResponse.json();
        const dtypes: Record<string, string> = dtypeData.dtypes;

        // Separate attributes into COLOR and TEXT
        setColorAttributes(attributes.filter(attr => dtypes[attr] === "RlvizType.COLOR"));
        setTextAttributes(attributes.filter(attr => dtypes[attr] === "RlvizType.TEXT"));
        setGridAttributes(attributes.filter(attr => dtypes[attr] === "RlvizType.GRID"));
      } catch (error) {
        console.error("Error fetching attributes:", error);
      }
    };

    fetchAttributes();
  }, []);

  // Toggles selection for attributes
  const toggleAttribute = (attr: string, isColor: boolean, isGrid: boolean) => {
    if (isColor) {
      setSelectedColorAttributes((prevSelected) =>
          prevSelected.includes(attr)
            ? prevSelected.filter((a) => a !== attr)
            : [...prevSelected, attr]
      );
    } else if (isGrid) {
      setSelectedGridAttributes((prevSelected) =>
          prevSelected.includes(attr)
            ? prevSelected.filter((a) => a !== attr)
            : [...prevSelected, attr]
      );
    } else {
      setSelectedTextAttributes((prevSelected) =>
        prevSelected.includes(attr)
          ? prevSelected.filter((a) => a !== attr) 
          : [...prevSelected, attr] 
      );
    }
  };


  return (
    <div style={{ padding: "10px", width: "200px" }}>
      <h3>Attributes</h3>

      {colorAttributes.length === 0 && textAttributes.length === 0 ? (
        <p>Loading...</p>
      ) : (
        <>
          {/* COLOR Attributes */}
          {colorAttributes.length > 0 && (
            <>
              <h4>Color Attributes</h4>
              {colorAttributes.map(attr => (
                <div key={attr}>
                  <input
                    type="checkbox"
                    checked={selectedColorAttributes.includes(attr)}
                    onChange={() => toggleAttribute(attr, true, false)}
                  />
                  <label>{attr}</label>
                </div>
              ))}
            </>
          )}

          {/* GRID Attributes */}
          {gridAttributes.length > 0 && (
              <>
                <h4>Grid Attributes</h4>
                {gridAttributes.map(attr => (
                    <div key={attr}>
                      <input
                          type="checkbox"
                          checked={selectedGridAttributes.includes(attr)}
                          onChange={() => toggleAttribute(attr, false, true)}
                      />
                      <label>{attr}</label>
                    </div>
                ))}
              </>
          )}

          {/* TEXT Attributes */}
          {textAttributes.length > 0 && (
            <>
              <h4>Text Attributes</h4>
              {textAttributes.map(attr => (
                <div key={attr}>
                  <input
                    type="checkbox"
                    checked={selectedTextAttributes.includes(attr)}
                    onChange={() => toggleAttribute(attr, false, false)}
                  />
                  <label>{attr}</label>
                </div>
              ))}
            </>
          )}
        </>
      )}
    </div>
  );
};

export default Sidebar;

