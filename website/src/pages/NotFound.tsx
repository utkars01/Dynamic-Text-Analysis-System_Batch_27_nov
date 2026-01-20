import { useNavigate, useLocation } from "react-router-dom";
import { useEffect } from "react";
import { motion } from "framer-motion";
import { Home, ArrowLeft, Compass } from "lucide-react";
import { Button } from "@/components/ui/button";
import PageLayout from "@/components/PageLayout";

const NotFound = () => {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    console.error("404 Error: User attempted to access non-existent route:", location.pathname);
  }, [location.pathname]);

  return (
    <PageLayout showFooter={false}>
      <div className="container mx-auto px-6 py-20">
        <div className="max-w-lg mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
          >
            <div className="w-24 h-24 rounded-3xl bg-gradient-to-br from-primary to-accent flex items-center justify-center mx-auto mb-8 shadow-glow">
              <Compass className="w-12 h-12 text-primary-foreground" />
            </div>
            <h1 className="text-6xl font-bold gradient-text mb-4">404</h1>
            <h2 className="text-2xl font-semibold text-foreground mb-4">Page Not Found</h2>
            <p className="text-lg text-muted-foreground mb-8">
              The page you're looking for doesn't exist or has been moved.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button variant="hero" size="lg" onClick={() => navigate("/")}>
                <Home className="w-5 h-5" />
                Go Home
              </Button>
              <Button variant="outline" size="lg" onClick={() => navigate(-1)}>
                <ArrowLeft className="w-5 h-5" />
                Go Back
              </Button>
            </div>
          </motion.div>
        </div>
      </div>
    </PageLayout>
  );
};

export default NotFound;
