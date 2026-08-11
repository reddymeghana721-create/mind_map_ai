import React, { useMemo, useCallback, useEffect } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  ReactFlowProvider
} from "@xyflow/react";
import CustomNode from "./CustomNode";

const nodeTypes = { customNode: CustomNode };

function FlowContent({
  initialNodes,
  initialEdges,
  selectedNodeId,
  onSelectNode,
  onToggleExpand
}) {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Keep React Flow nodes and edges in sync with prop updates
  useEffect(() => {
    const nodesWithCallbacks = initialNodes.map((n) => ({
      ...n,
      draggable: false,
      data: {
        ...n.data,
        onToggle: onToggleExpand
      }
    }));
    setNodes(nodesWithCallbacks);
    setEdges(initialEdges);
  }, [initialNodes, initialEdges, onToggleExpand, setNodes, setEdges]);

  // Handle node selection click without panning or zooming viewport
  const onNodeClick = useCallback(
    (_, node) => {
      onSelectNode(node.id);
    },
    [onSelectNode]
  );

  return (
    <div className="w-full h-full relative overflow-hidden bg-slate-950">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable={true}
        panOnDrag={true}
        zoomOnScroll={true}
        zoomOnPinch={true}
        panOnScroll={false}
        minZoom={0.2}
        maxZoom={2}
        defaultEdgeOptions={{
          type: "smoothstep",
          animated: false
        }}
        className="touch-none"
      >
        <Background color="#334155" gap={24} size={1} />
        <Controls position="bottom-left" showInteractive={false} />
        <MiniMap
          position="bottom-right"
          nodeColor={(node) => node.data?.color?.border || "#0ea5e9"}
          maskColor="rgba(15, 23, 42, 0.7)"
          zoomable
          pannable
        />
      </ReactFlow>
    </div>
  );
}

export default function MindMapFlow(props) {
  return (
    <ReactFlowProvider>
      <FlowContent {...props} />
    </ReactFlowProvider>
  );
}
