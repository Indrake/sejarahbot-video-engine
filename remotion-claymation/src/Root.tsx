import React from "react";
import { Composition } from "remotion";

const DisasterShorts: React.FC = () => {
  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        backgroundColor: "#d8c49a",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        flexDirection: "column",
        fontFamily: "Arial",
        color: "#493522",
      }}
    >
      <div style={{ fontSize: 76, fontWeight: "bold" }}>
        DISASTER LAB
      </div>
      <div style={{ fontSize: 38, marginTop: 24 }}>
        Claymation Diorama
      </div>
    </div>
  );
};

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="DisasterShorts"
      component={DisasterShorts}
      durationInFrames={1500}
      fps={30}
      width={1080}
      height={1920}
    />
  );
};
