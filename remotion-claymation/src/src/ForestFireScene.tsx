import React from "react";
import { useCurrentFrame } from "remotion";

export const ForestFireScene: React.FC = () => {
  const frame = useCurrentFrame();
  const flameScale = 1 + Math.sin(frame * 0.25) * 0.08;
  const smokeShift = Math.sin(frame * 0.06) * 12;

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        position: "relative",
        overflow: "hidden",
        background: "linear-gradient(#d9c49b, #f0d9a6)",
      }}
    >
      <div style={{
        position: "absolute",
        top: "12%",
        left: "8%",
        color: "#59452e",
        fontSize: 54,
        fontWeight: "bold",
      }}>
        KEBakaran HUTAN
      </div>

      <svg
        viewBox="0 0 1080 1500"
        style={{
          position: "absolute",
          width: "100%",
          height: "85%",
          bottom: 0,
        }}
      >
        <path d="M0 1150 Q250 1000 500 1140 T1080 1100 L1080 1500 L0 1500Z"
          fill="#795638" />

        <g fill="#557044" stroke="#405536" strokeWidth="14">
          <path d="M100 1080 L180 650 L260 1080Z" />
          <path d="M230 1100 L340 540 L450 1100Z" />
          <path d="M650 1080 L750 590 L850 1080Z" />
          <path d="M820 1100 L920 680 L1020 1100Z" />
        </g>

        <g fill="#765039">
          <rect x="165" y="1040" width="35" height="230" rx="12" />
          <rect x="325" y="1040" width="35" height="230" rx="12" />
          <rect x="735" y="1040" width="35" height="230" rx="12" />
          <rect x="905" y="1040" width="35" height="230" rx="12" />
        </g>

        <g transform={`translate(${smokeShift},0)`} fill="#77716a" opacity="0.8">
          <circle cx="480" cy="700" r="90" />
          <circle cx="570" cy="620" r="120" />
          <circle cx="680" cy="540" r="105" />
        </g>

        <g transform={`translate(0,1050) scale(1,${flameScale})`}
          transformOrigin="540px 1050px">
          <path d="M440 300 Q350 150 480 0 Q470 160 560 80 Q680 190 590 300Z"
            fill="#e65b24" />
          <path d="M490 300 Q450 190 540 110 Q550 210 600 300Z"
            fill="#f5a623" />
          <path d="M525 300 Q510 230 555 185 Q570 250 565 300Z"
            fill="#ffe18a" />
        </g>
      </svg>
    </div>
  );
};
