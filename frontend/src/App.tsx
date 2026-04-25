import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { lazy, Suspense } from "react";
import { AppLayout } from "@/components/layout/AppLayout";
import { ErrorBoundary } from "@/components/shared/ErrorBoundary";
import { useWebSocket } from "@/hooks/useWebSocket";
import { Toaster } from "@/components/ui/toaster";
import { NotificationBridge } from "@/components/shared/NotificationBridge";

const Dashboard = lazy(() => import("@/pages/Dashboard"));
const ProjectList = lazy(() => import("@/pages/ProjectList"));
const PipelineView = lazy(() => import("@/pages/PipelineView"));
const StageReview = lazy(() => import("@/pages/StageReview"));
const ProjectSettings = lazy(() => import("@/pages/ProjectSettings"));
const NodeManager = lazy(() => import("@/pages/NodeManager"));
const SupplierConfig = lazy(() => import("@/pages/SupplierConfig"));
const Settings = lazy(() => import("@/pages/Settings"));

function LoadingFallback() {
  return (
    <div className="flex items-center justify-center h-full">
      <div className="text-muted-foreground">加载中...</div>
    </div>
  );
}

function AppInner() {
  useWebSocket();
  return (
    <>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<Navigate to="/projects" replace />} />
          <Route path="/dashboard" element={<Suspense fallback={<LoadingFallback />}><Dashboard /></Suspense>} />
          <Route path="/projects" element={<Suspense fallback={<LoadingFallback />}><ProjectList /></Suspense>} />
          <Route path="/projects/:id" element={<Navigate to="pipeline" replace />} />
          <Route path="/projects/:id/pipeline" element={<Suspense fallback={<LoadingFallback />}><PipelineView /></Suspense>} />
          <Route path="/projects/:id/stages/:stageType" element={<Suspense fallback={<LoadingFallback />}><StageReview /></Suspense>} />
          <Route path="/projects/:id/settings" element={<Suspense fallback={<LoadingFallback />}><ProjectSettings /></Suspense>} />
          <Route path="/nodes" element={<Suspense fallback={<LoadingFallback />}><NodeManager /></Suspense>} />
          <Route path="/suppliers" element={<Suspense fallback={<LoadingFallback />}><SupplierConfig /></Suspense>} />
          <Route path="/settings" element={<Suspense fallback={<LoadingFallback />}><Settings /></Suspense>} />
        </Route>
      </Routes>
      <NotificationBridge />
      <Toaster />
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <ErrorBoundary>
        <AppInner />
      </ErrorBoundary>
    </BrowserRouter>
  );
}