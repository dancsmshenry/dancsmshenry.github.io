#!/usr/bin/env bash
# Build all article figures.
#
# Figure 1 is the ditaa composition schematic; figures 2-16 are
# 4-bytes-per-row Pillow structure grids.  ditaa is rendered one file at a
# time because PlantUML's ditaa renderer has crashed when several files were
# rendered in parallel.
set -euo pipefail

cd "$(dirname "$0")"

JAR=""
if [[ -n "${PLANTUML_JAR:-}" && -f "${PLANTUML_JAR}" ]]; then
  JAR="$PLANTUML_JAR"
elif [[ -f "plantuml.jar" ]]; then
  JAR="plantuml.jar"
elif [[ -f "/tmp/ditaa_probe/plantuml.jar" ]]; then
  JAR="/tmp/ditaa_probe/plantuml.jar"
fi

# Figure 1: overall composition (ditaa, needs PlantUML).
python3 build_ditaa_sources.py
if [[ -n "$JAR" ]]; then
  echo "Using PlantUML: $JAR"
  java -jar "$JAR" -tpng fig01-message-overview.puml
else
  echo "PlantUML jar not found; keeping the existing fig01-message-overview.png."
  echo "Set PLANTUML_JAR=/path/to/plantuml.jar to regenerate it."
fi

# Figures 2-16: 4-bytes-per-row structure grids (Pillow only).
python3 build_grid_figures.py

echo "Done. Images, scripts and puml sources are in this folder."
