#!/bin/bash
# Trigger pipeline via git push

# Configure git if needed (for CI envs)
# git config user.email "bot@example.com"
# git config user.name "Demo Bot"

# Modify a file
echo "# Updated at $(date)" >> README.md

# Commit and Push
git add README.md
git commit -m "Trigger pipeline test at $(date)"
git push origin main

echo "Pipeline triggered! Check CodePipeline console."
