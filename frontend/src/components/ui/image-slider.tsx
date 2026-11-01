import * as React from "react";
import { AnimatePresence, motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface ImageSliderProps extends React.HTMLAttributes<HTMLDivElement> {
  images: string[];
  interval?: number;
}

const ImageSlider = React.forwardRef<HTMLDivElement, ImageSliderProps>(
  ({ images, interval = 4500, className, ...props }, ref) => {
    const [currentIndex, setCurrentIndex] = React.useState(0);

    // Auto-advance slide smoothly
    React.useEffect(() => {
      if (!images || images.length <= 1) return;
      const timer = setInterval(() => {
        setCurrentIndex((prevIndex) =>
          prevIndex === images.length - 1 ? 0 : prevIndex + 1
        );
      }, interval);

      return () => clearInterval(timer);
    }, [images, interval]);

    if (!images || images.length === 0) return null;

    return (
      <div
        ref={ref}
        className={cn(
          "relative w-full h-full overflow-hidden bg-neutral-950 select-none",
          className
        )}
        {...props}
      >
        {/* Smooth Crossfade + Gentle Zoom Slider */}
        <AnimatePresence mode="popLayout" initial={false}>
          <motion.div
            key={currentIndex}
            initial={{ opacity: 0, scale: 1.06 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.98 }}
            transition={{
              duration: 1.1,
              ease: [0.22, 1, 0.36, 1],
            }}
            className="absolute inset-0 w-full h-full"
          >
            <img
              src={images[currentIndex]}
              alt={`Farmer slide ${currentIndex + 1}`}
              className="w-full h-full object-cover object-center pointer-events-none"
              loading="eager"
            />
            {/* Cinematic dark gradient protection for overlay text and dots */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/85 via-black/30 to-black/40 pointer-events-none" />
          </motion.div>
        </AnimatePresence>

        {/* 21st.dev Smooth Carousel Interactive Dots Capsule */}
        <div className="absolute bottom-5 left-1/2 -translate-x-1/2 z-30 flex items-center gap-2 px-3 py-1.5 rounded-full bg-black/45 backdrop-blur-md border border-white/20 shadow-xl pointer-events-auto">
          {images.map((_, index) => {
            const isActive = currentIndex === index;
            return (
              <button
                key={index}
                type="button"
                onClick={() => setCurrentIndex(index)}
                className={cn(
                  "relative h-2 rounded-full transition-all duration-400 ease-out cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-white",
                  isActive
                    ? "w-6 bg-white shadow-[0_0_10px_rgba(255,255,255,0.9)]"
                    : "w-2 bg-white/40 hover:bg-white/80 hover:scale-125"
                )}
                aria-label={`Go to slide ${index + 1}`}
                aria-current={isActive ? "true" : undefined}
              />
            );
          })}
        </div>
      </div>
    );
  }
);

ImageSlider.displayName = "ImageSlider";

export { ImageSlider };
