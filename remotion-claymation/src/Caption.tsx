import React from "react";
import { useCurrentFrame } from "remotion";

const captions = [
  { start: 0, end: 150, text: "Hutan terbakar, kehidupan terancam." },
  { start: 150, end: 330, text: "Api dapat menyebar dengan sangat cepat." },
  { start: 330, end: 540, text: "Panas dan angin memperluas kebakaran." },
  { start: 540, end: 900, text: "Habitat satwa dan ekosistem ikut rusak." },
  { start: 900, end: 1200, text: "Pemulihan hutan bisa membutuhkan waktu lama." },
  { start: 1200, end: 1500, text: "Melindungi hutan berarti melindungi kehidupan." }
];

export const Caption: React.FC = () => {
  const frame = useCurrentFrame();
  const current = captions.find(
    (item) => frame >= item.start && frame < item.end
  );

  if (!current) return null;

  return (
    <div
      style={{
        position: "absolute",
        bottom: "12%",
        width: "86%",
        left: "7%",
        textAlign: "center",
        color: "white",
        fontSize: 48,
        fontWeight: "bold",
        lineHeight: 1.3,
        textShadow: "2px 3px 5px #24180f",
        backgroundColor: "rgba(45, 31, 20, 0.72)",
        padding: "22px",
        borderRadius: 18
      }}
    >
      {current.text}
    </div>
  );
};
