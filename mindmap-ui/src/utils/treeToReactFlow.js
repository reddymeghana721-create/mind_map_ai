/**
 * Utility to convert nested JSON tree structure into React Flow nodes and edges
 */

export function convertTreeToReactFlow(treeData, expandedNodeIds, selectedNodeId = null) {
  if (!treeData) return { nodes: [], edges: [] };

  const nodes = [];
  const edges = [];
  const activePathNodeIds = new Set();

  // Helper to trace ancestor path of selected node
  function findSelectedPath(node, path = []) {
    if (!node) return false;
    const currentPath = [...path, node.id];
    if (node.id === selectedNodeId) {
      currentPath.forEach((id) => activePathNodeIds.add(id));
      return true;
    }
    for (const child of node.children || []) {
      if (findSelectedPath(child, currentPath)) {
        return true;
      }
    }
    return false;
  }

  if (selectedNodeId) {
    findSelectedPath(treeData);
  }

  // Spacious layout parameters for clean readability
  const X_SPACING = 320;
  const Y_ROW_HEIGHT = 120;

  let globalYCounter = 0;

  function traverse(node, depth = 0, parentId = null) {
    if (!node) return;

    const isExpanded = expandedNodeIds.has(node.id);
    const children = node.children || [];
    const hasChildren = children.length > 0;
    const isSelected = node.id === selectedNodeId;
    const isInActivePath = activePathNodeIds.has(node.id);

    // Calculate Y position using subtree layout
    let yPos = globalYCounter * Y_ROW_HEIGHT;

    if (!hasChildren || !isExpanded) {
      globalYCounter += 1;
    }

    const childYPositions = [];

    if (hasChildren && isExpanded) {
      children.forEach((child) => {
        const childY = traverse(child, depth + 1, node.id);
        childYPositions.push(childY);
      });
      if (childYPositions.length > 0) {
        yPos = (childYPositions[0] + childYPositions[childYPositions.length - 1]) / 2;
      }
    }

    // Build React Flow Node
    nodes.push({
      id: node.id,
      type: "customNode",
      position: { x: depth * X_SPACING, y: yPos },
      draggable: false,
      data: {
        id: node.id,
        label: node.label || "Untitled Concept",
        summary: node.summary || "No description available.",
        video: node.video || node.video_url || (node.ui && node.ui.video),
        hasVideo: Boolean(node.video || node.video_url || (node.ui && (node.ui.video || node.ui.has_video))),
        nodeType: node.type || (depth === 0 ? "chapter" : depth === 1 ? "theme" : depth === 2 ? "section" : "concept"),
        depth: depth,
        hasChildren: hasChildren,
        isExpanded: isExpanded,
        isSelected: isSelected,
        isInActivePath: isInActivePath,
        rawNode: node
      }
    });

    // Build React Flow Edge from Parent
    if (parentId) {
      const isEdgeActive = isInActivePath && activePathNodeIds.has(parentId);
      edges.push({
        id: `e-${parentId}-${node.id}`,
        source: parentId,
        target: node.id,
        type: "smoothstep",
        animated: isEdgeActive,
        style: {
          stroke: isEdgeActive ? "#38bdf8" : "#1e293b",
          strokeWidth: isEdgeActive ? 1.5 : 1,
          opacity: isEdgeActive ? 1 : 0.4,
          transition: "all 0.2s ease"
        }
      });
    }

    return yPos;
  }

  traverse(treeData, 0, null);

  return { nodes, edges };
}
