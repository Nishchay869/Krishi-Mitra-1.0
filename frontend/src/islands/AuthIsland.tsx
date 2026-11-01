import type { Variants } from "framer-motion";
import { motion } from "framer-motion";
import { ImageSlider } from "@/components/ui/image-slider";
import { ArrowLeft } from "lucide-react";
import "./AuthIsland.css";

export interface AuthIslandProps {
  mode?: "login" | "register";
  csrfToken?: string;
  nextUrl?: string;
  actionUrl?: string;
  errorMessage?: string;
  loginUrl?: string;
  registerUrl?: string;
  images?: string[];
}

function GoogleIcon({ className = "h-4 w-4" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
      <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
      <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" fill="#FBBC05" />
      <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" fill="#EA4335" />
    </svg>
  );
}

function AppleIcon({ className = "h-4 w-4" }: { className?: string }) {
  return (
    <svg className={`${className} auth-apple-icon`} viewBox="0 0 24 24">
      <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M15.97 6.38c.62-.76 1.05-1.81.93-2.88-.92.04-2.02.62-2.67 1.38-.58.67-1.09 1.74-.95 2.78 1.02.08 2.07-.52 2.69-1.28z" />
    </svg>
  );
}

const defaultImages = [
  "/static/images/auth/farmer-1.jpg",
  "/static/images/auth/farmer-2.jpg",
  "/static/images/auth/farmer-3.jpg",
  "/static/images/auth/farmer-4.jpg",
];

export default function AuthIsland({
  mode = "login",
  csrfToken = "",
  nextUrl = "/",
  actionUrl = "/accounts/login/",
  errorMessage = "",
  loginUrl = "/accounts/login/",
  registerUrl = "/accounts/register/",
  images = defaultImages,
}: AuthIslandProps) {
  const isLogin = mode === "login";

  const containerVariants: Variants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.12,
      },
    },
  };

  const itemVariants: Variants = {
    hidden: { y: 12, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: "spring" as const,
        stiffness: 120,
        damping: 14,
      },
    },
  };

  const slideImages = images && images.length > 0 ? images : defaultImages;

  return (
    <div className="w-full min-h-[580px] md:h-screen flex items-center justify-center p-2 sm:p-4">
      <motion.div
        className="auth-card w-full max-w-5xl h-[560px] sm:h-[640px] md:h-[720px] flex flex-row rounded-2xl overflow-hidden"
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.45, ease: "easeOut" }}
      >
        {/* Left column: Photo Slider (Horizontal Even on Mobile) */}
        <div className="auth-slider-panel w-5/12 sm:w-1/2 h-full relative overflow-hidden flex-shrink-0">
          <ImageSlider
            images={slideImages}
            interval={4500}
            className="h-full w-full"
          />

          {/* Frosted Glass Back Button on Photo */}
          <div className="absolute top-4 left-4 z-30">
            <a
              href="/"
              className="auth-photo-back-btn"
              title="Return to home page"
            >
              <ArrowLeft size={13} />
              <span>Back to home</span>
            </a>
          </div>

          {/* Photo Caption Overlay (Pure White Typography) */}
          <div className="auth-photo-caption absolute bottom-8 left-6 right-6 z-20 pointer-events-none hidden sm:block">
            <span className="auth-photo-pill">
              Krishi Mitra
            </span>
            <h2 className="auth-photo-title">
              Empowering India's Farmers
            </h2>
            <p className="auth-photo-desc">
              Intelligent crop advisory, real-time weather & mandi market intelligence.
            </p>
          </div>
        </div>

        {/* Right column: Login / Register Form Panel */}
        <div className="auth-form-panel w-7/12 sm:w-1/2 h-full flex flex-col items-center justify-center p-4 sm:p-8 md:p-12 overflow-y-auto">
          <motion.div
            className="w-full max-w-sm"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            {/* Header: Back Button + Brand cue */}
            <motion.div variants={itemVariants} className="flex items-center justify-between w-full mb-3 sm:mb-5">
              <a
                href="/"
                className="auth-back-link"
                title="Return to home"
              >
                <ArrowLeft size={13} />
                <span>Back</span>
              </a>
              <span className="auth-brand-cue">
                Krishi Mitra
              </span>
            </motion.div>

            {/* Typography Header */}
            <motion.div variants={itemVariants} className="mb-4 sm:mb-6">
              <h1 className="auth-title">
                {isLogin ? "Welcome Back" : "Create Account"}
              </h1>
              <p className="auth-subtitle">
                {isLogin
                  ? "Enter your credentials to access your account."
                  : "Join Krishi Mitra for personalized farming assistance."}
              </p>
            </motion.div>

            {/* Error Message */}
            {errorMessage && (
              <motion.div
                variants={itemVariants}
                className="mb-4 p-3 rounded-xl text-xs sm:text-sm font-medium bg-red-50 text-red-700 border border-red-200 dark:bg-red-950/60 dark:text-red-300 dark:border-red-800"
              >
                {errorMessage}
              </motion.div>
            )}

            {/* Social OAuth Buttons */}
            <motion.div variants={itemVariants} className="grid grid-cols-2 gap-3 mb-5">
              <button
                type="button"
                className="auth-social-btn"
                onClick={() => alert("Google Sign-In is configured via administrator.")}
              >
                <GoogleIcon className="h-4 w-4 flex-shrink-0" />
                <span>Google</span>
              </button>
              <button
                type="button"
                className="auth-social-btn"
                onClick={() => alert("Apple Sign-In is configured via administrator.")}
              >
                <AppleIcon className="h-4 w-4 flex-shrink-0" />
                <span>Apple</span>
              </button>
            </motion.div>

            {/* Divider */}
            <motion.div variants={itemVariants} className="auth-divider-wrap mb-5">
              <div className="auth-divider-line" />
              <div className="auth-divider-text-wrap">
                <span className="auth-divider-text">Or continue with email</span>
              </div>
            </motion.div>

            {/* Credentials Form */}
            <motion.form
              variants={itemVariants}
              method="POST"
              action={actionUrl}
              className="space-y-4"
            >
              <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />
              <input type="hidden" name="next" value={nextUrl} />

              <div className="space-y-1.5">
                <label
                  htmlFor="auth-email"
                  className="auth-label"
                >
                  Email
                </label>
                <input
                  id="auth-email"
                  name="email"
                  type="email"
                  placeholder="farmer@example.com"
                  required
                  autoComplete="username"
                  className="auth-input"
                />
              </div>

              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <label
                    htmlFor="auth-password"
                    className="auth-label"
                  >
                    Password
                  </label>
                  {isLogin && (
                    <a
                      href="#forgot"
                      onClick={(e) => {
                        e.preventDefault();
                        alert("Password reset is managed by your administrator or farm support.");
                      }}
                      className="auth-forgot-link"
                    >
                      Forgot password?
                    </a>
                  )}
                </div>
                <input
                  id="auth-password"
                  name="password"
                  type="password"
                  placeholder="••••••••"
                  required
                  autoComplete={isLogin ? "current-password" : "new-password"}
                  className="auth-input"
                />
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                className="auth-submit-btn"
              >
                <span>{isLogin ? "Sign In" : "Create Account"}</span>
              </button>
            </motion.form>

            {/* Bottom Switch Link */}
            <motion.p
              variants={itemVariants}
              className="auth-switch-text"
            >
              {isLogin ? (
                <>
                  <span>Don't have an account?</span>{" "}
                  <a
                    href={registerUrl}
                    className="auth-switch-link"
                  >
                    Sign up
                  </a>
                </>
              ) : (
                <>
                  <span>Already have an account?</span>{" "}
                  <a
                    href={loginUrl}
                    className="auth-switch-link"
                  >
                    Sign in
                  </a>
                </>
              )}
            </motion.p>
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
}
