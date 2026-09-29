import { useEffect, useRef } from "react";
import "./GlobalBackground.css";

function getDepthColor(i, totalDepth) {
  const t = (i - 1) / Math.max(1, totalDepth - 1);

  const wave = Math.sin(t * Math.PI);

  const r = Math.round(255 - wave * 170);
  const g = Math.round(244 - wave * 200);
  const b = Math.round(201 - wave * 195);

  return `rgb(${r}, ${g}, ${b})`;
}

function Scene({ type, text }) {
  const rootRef = useRef(null);

  useEffect(() => {
    const root = rootRef.current;

    if (!root) return;

    const front = root.querySelector(".text-layer.front");
    const highlight = root.querySelector(".text-layer.highlight");

    const depth = text === "CONTRIBPILOT" ? 42 : 34;

    // Remove old depth layers.
    // This also prevents duplicate layers in React StrictMode.
    root
      .querySelectorAll(".text-layer.depth")
      .forEach((element) => element.remove());

    // Create 3D depth layers
    for (let i = 1; i <= depth; i++) {
      const layer = document.createElement("div");

      layer.className = "text-layer depth";
      layer.textContent = text;

      layer.style.setProperty("--z", `${-i}px`);
      layer.style.setProperty(
        "--layer-color",
        getDepthColor(i, depth)
      );

      root.appendChild(layer);
    }

    // Front layer
    if (front) {
      front.style.setProperty("--z", "0px");
      front.style.setProperty(
        "--layer-color",
        "rgba(255, 240, 180, 1)"
      );
    }

    // Highlight layer
    if (highlight) {
      highlight.style.setProperty("--z", "1px");
    }
  }, [text]);

  return (
    <div className={`scene ${type}`}>
      <div className="text-3d" ref={rootRef}>
        {/* Gold blurred aura */}
        <div className="gold-aura">{text}</div>

        {/* Deep shadow */}
        <div className="text-shadow">{text}</div>

        {/* Main 3D front */}
        <div className="text-layer front">{text}</div>

        {/* Highlight */}
        <div className="text-layer highlight">{text}</div>
      </div>
    </div>
  );
}

export default function GlobalBackground() {
  return (
    <div
      className="global-bg-root"
      aria-hidden="true"
    >
      {/* Main dark background */}
      <div className="ambient-background" />

      {/* Moving ambient lights */}
      <div className="ambient-light one" />
      <div className="ambient-light two" />

      {/* Glass spheres */}
      <div className="glass-orbs">
        <div className="glass-orb one" />
        <div className="glass-orb two" />
        <div className="glass-orb three" />
      </div>

      {/* Subtle grid */}
      <div className="grid" />

      {/* Film/grain effect */}
      <div className="glass-grain" />

      {/* Animated 3D text */}
      <div className="scene-container">
        <Scene
          type="contrib"
          text="CONTRIBPILOT"
        />

        <Scene
          type="compile"
          text="CompileSyntaxError"
        />
      </div>
    </div>
  );
}