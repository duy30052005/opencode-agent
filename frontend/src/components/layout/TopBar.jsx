import { useNavigate, useLocation } from "react-router-dom";
import MaterialIcon from "../ui/MaterialIcon";

const TAB_LINKS = [
  { label: "Workflow", path: "/" },
  { label: "Editor", path: "/workspace" },
  { label: "Terminal", path: "/status" },
  { label: "Logs", path: "/history" },
];

/**
 * TopBar — sticky top navigation bar.
 * @param {string}           [title]     - Page title shown on desktop (e.g. "Fibonacci…")
 * @param {boolean}          [showTabs]  - Show Workflow/Editor/Terminal/Logs tabs
 * @param {string}           [activeTab] - Which tab is active (label)
 * @param {React.ReactNode}  [statusBadge] - Optional left-side status badge slot
 * @param {boolean}          [showActions] - Show Share + Execute buttons
 * @param {function}         [onShare]
 * @param {function}         [onExecute]
 */
export default function TopBar({
  title,
  showTabs = true,
  activeTab = "Workflow",
  statusBadge,
  showActions = true,
  onShare,
  onExecute,
}) {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <header className="flex justify-between items-center px-gutter h-16 w-full z-40 bg-surface-container/80 backdrop-blur-md border-b border-white/10 sticky top-0">
      {/* Left */}
      <div className="flex items-center gap-4">
        {/* Mobile hamburger */}
        <button className="md:hidden text-on-surface-variant hover:text-on-surface p-2">
          <MaterialIcon icon="menu" />
        </button>

        {/* Mobile brand */}
        <div className="md:hidden font-headline-md text-headline-md font-bold text-on-surface">
          OpenCode Agent
        </div>

        {/* Desktop: title or tabs */}
        {title ? (
          <div className="hidden md:flex items-center gap-6">
            <h2 className="font-headline-md text-headline-md font-bold text-on-surface tracking-tight truncate">
              {title}
            </h2>
            {statusBadge && (
              <div className="flex items-center gap-4 border-l border-outline-variant pl-6">
                {statusBadge}
              </div>
            )}
          </div>
        ) : (
          showTabs && (
            <nav className="hidden md:flex items-center gap-6 h-full pt-4">
              {TAB_LINKS.map((tab) => {
                const isActive = tab.label === activeTab;
                return (
                  <a
                    key={tab.label}
                    href={tab.path}
                    onClick={(e) => {
                      e.preventDefault();
                      navigate(tab.path);
                    }}
                    className={`pb-4 font-body-sm text-body-sm hover:text-primary transition-all cursor-pointer active:opacity-70 border-b-2 ${
                      isActive
                        ? "text-primary font-bold border-primary"
                        : "text-on-surface-variant border-transparent"
                    }`}
                  >
                    {tab.label}
                  </a>
                );
              })}
            </nav>
          )
        )}

        {/* Title page: tab nav next to title */}
        {title && showTabs && (
          <nav className="hidden md:flex items-center gap-6 h-full pt-4">
            {TAB_LINKS.map((tab) => {
              const isActive = tab.label === activeTab;
              return (
                <a
                  key={tab.label}
                  href={tab.path}
                  onClick={(e) => {
                    e.preventDefault();
                    navigate(tab.path);
                  }}
                  className={`pb-4 pt-4 font-body-sm text-body-sm transition-all ${
                    isActive
                      ? "text-primary font-bold border-b-2 border-primary"
                      : "text-on-surface-variant hover:text-on-surface"
                  }`}
                >
                  {tab.label}
                </a>
              );
            })}
          </nav>
        )}
      </div>

      {/* Right */}
      <div className="flex items-center gap-4">
        {showActions && (
          <div className="hidden lg:flex items-center gap-2 mr-4">
            <button
              onClick={onShare}
              className="px-4 py-1.5 rounded-md border border-white/10 text-on-surface-variant font-body-sm text-body-sm hover:bg-white/5 transition-colors"
            >
              Share
            </button>
            <button
              onClick={onExecute}
              className="px-4 py-1.5 rounded-md bg-primary/10 text-primary border border-primary/20 font-body-sm text-body-sm hover:bg-primary/20 transition-colors flex items-center gap-2"
            >
              <MaterialIcon icon="play_arrow" size={18} />
              Execute
            </button>
          </div>
        )}

        {/* Right side (Actions & Profile) */}
        <div className="flex items-center gap-4">
          {/* Token Tracker (Task 16) */}
          <div className="hidden sm:flex items-center gap-2 bg-surface-container/50 px-3 py-1.5 rounded-full border border-white/5">
            <MaterialIcon icon="token" className="text-secondary" size={16} />
            <div className="flex flex-col">
              <span className="font-code-base text-[10px] text-on-surface-variant leading-none">
                TOKENS
              </span>
              <span className="font-code-base text-xs text-on-surface font-bold leading-none mt-0.5">
                24.5k{" "}
                <span className="text-on-surface-variant font-normal">
                  ($0.12)
                </span>
              </span>
            </div>
          </div>

          <button className="relative p-2 rounded-full hover:bg-white/10 text-on-surface-variant transition-colors group">
            <MaterialIcon icon="notifications" />
            <span className="absolute top-2 right-2 w-2 h-2 bg-primary rounded-full border border-surface shadow-[0_0_8px_rgba(192,193,255,0.6)]" />
          </button>
          <button className="p-1 hover:opacity-80 transition-opacity ml-2">
            <img
              alt="User Profile"
              className="w-8 h-8 rounded-full border border-white/20"
              src="../../assets/avatar-person.svg"
            />
          </button>
        </div>
      </div>
    </header>
  );
}
