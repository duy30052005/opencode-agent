import TopBar from '../layout/TopBar'
import MetricCard from '../ui/MetricCard'
import BarItem from '../ui/BarItem'

const LANG_DIST = [
  { language: 'Python',     percent: 45, barColor: 'bg-primary',             glowColor: 'rgba(192,193,255,0.4)' },
  { language: 'TypeScript', percent: 30, barColor: 'bg-secondary',           glowColor: 'rgba(78,222,163,0.4)' },
  { language: 'Go',         percent: 15, barColor: 'bg-primary-container' },
  { language: 'Rust',       percent: 10, barColor: 'bg-tertiary-container' },
]

export default function AnalyticsPage() {
  return (
    <>
      <TopBar showTabs={false} />

      <main className="pt-8 min-h-screen p-container-padding">
          <div className="max-w-[1600px] mx-auto">
            {/* Page Header */}
            <div className="mb-10 flex flex-col gap-2">
              <h2 className="font-display-lg text-display-lg text-on-surface">Performance Analytics</h2>
              <p className="font-body-base text-body-base text-on-surface-variant">
                System overview and execution metrics for the current billing period.
              </p>
            </div>

            {/* Top Metrics Bento Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-node-gap mb-node-gap">
              <MetricCard
                label="Total Sessions"
                value="1,248"
                icon="chat"
                iconColor="text-primary"
                barColor="bg-primary"
                barWidth={75}
                trend="+12%"
                trendUp={true}
              />
              <MetricCard
                label="Success Rate"
                value="94.2"
                unit="%"
                icon="check_circle"
                iconColor="text-secondary"
                barColor="bg-secondary"
                barWidth={94}
                trend="+2.1%"
                trendUp={true}
              />
              <MetricCard
                label="Avg Execution Time"
                value="1.4"
                unit="s"
                icon="timer"
                iconColor="text-tertiary-container"
                barColor="bg-tertiary-container"
                barWidth={33}
                trend="-0.3s"
                trendUp={false}
                trendColor="text-tertiary-container"
                trendBg="bg-tertiary-container/10"
              />
              <MetricCard
                label="Total Tokens Used"
                value="4.2"
                unit="M"
                icon="memory"
                iconColor="text-primary-container"
                barContent={
                  <div className="flex gap-1 h-full w-full">
                    <div className="h-full bg-primary w-1/2" />
                    <div className="h-full bg-secondary w-1/4" />
                    <div className="h-full bg-tertiary-container w-1/4" />
                  </div>
                }
              />
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-node-gap">
              {/* Line Chart: Success Rate Over Time */}
              <div className="glass-card rounded-xl p-6 lg:col-span-2 relative group">
                <div className="flex justify-between items-center mb-6">
                  <div>
                    <h3 className="font-headline-md text-headline-md text-on-surface">Execution Success Rate</h3>
                    <p className="font-body-sm text-body-sm text-on-surface-variant">Daily aggregation over the last 7 days</p>
                  </div>
                  <div className="flex gap-2 bg-surface-container rounded-lg p-1 border border-white/5">
                    <button className="px-3 py-1 font-body-sm text-body-sm text-on-surface bg-white/10 rounded shadow-sm">7D</button>
                    <button className="px-3 py-1 font-body-sm text-body-sm text-on-surface-variant hover:text-on-surface transition-colors">30D</button>
                    <button className="px-3 py-1 font-body-sm text-body-sm text-on-surface-variant hover:text-on-surface transition-colors">All</button>
                  </div>
                </div>

                {/* Chart Graphic Mockup */}
                <div className="h-[300px] w-full relative flex items-end border-l border-b border-white/10 pb-6 pl-4">
                  {/* Y Axis Labels */}
                  <div className="absolute left-[-2rem] top-0 bottom-6 flex flex-col justify-between font-code-base text-code-base text-on-surface-variant text-xs h-full py-2">
                    <span>100%</span>
                    <span>75%</span>
                    <span>50%</span>
                    <span>25%</span>
                  </div>
                  {/* Grid Lines */}
                  <div className="absolute inset-0 flex flex-col justify-between pb-6 pl-4 opacity-10 pointer-events-none">
                    <div className="w-full border-b border-white border-dashed" />
                    <div className="w-full border-b border-white border-dashed" />
                    <div className="w-full border-b border-white border-dashed" />
                    <div className="w-full border-b border-white border-dashed" />
                  </div>
                  {/* SVG Line Curve */}
                  <svg className="absolute inset-0 h-[calc(100%-1.5rem)] w-[calc(100%-1rem)] ml-4 pointer-events-none overflow-visible" preserveAspectRatio="none" viewBox="0 0 100 100">
                    <defs>
                      <linearGradient id="glow" x1="0%" x2="0%" y1="0%" y2="100%">
                        <stop offset="0%" stopColor="#4edea3" stopOpacity="0.3" />
                        <stop offset="100%" stopColor="#4edea3" stopOpacity="0" />
                      </linearGradient>
                    </defs>
                    <path d="M0,80 Q10,60 20,40 T40,20 T60,10 T80,15 T100,5 L100,100 L0,100 Z" fill="url(#glow)" />
                    <path d="M0,80 Q10,60 20,40 T40,20 T60,10 T80,15 T100,5" fill="none" stroke="#4edea3" strokeWidth="2" style={{ filter: 'drop-shadow(0 0 8px rgba(78, 222, 163, 0.6))' }} />
                    <circle cx="0" cy="80" fill="#131313" r="3" stroke="#4edea3" strokeWidth="2" />
                    <circle cx="20" cy="40" fill="#131313" r="3" stroke="#4edea3" strokeWidth="2" />
                    <circle cx="40" cy="20" fill="#131313" r="3" stroke="#4edea3" strokeWidth="2" />
                    <circle cx="60" cy="10" fill="#131313" r="3" stroke="#4edea3" strokeWidth="2" />
                    <circle cx="80" cy="15" fill="#131313" r="3" stroke="#4edea3" strokeWidth="2" />
                    <circle cx="100" cy="5" fill="#131313" r="3" stroke="#4edea3" strokeWidth="2" />
                  </svg>
                  {/* X Axis Labels */}
                  <div className="absolute bottom-[-1.5rem] left-4 right-0 flex justify-between font-code-base text-code-base text-on-surface-variant text-xs px-2">
                    <span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span><span>Sun</span>
                  </div>
                </div>
              </div>

              {/* Bar Chart: Languages Used */}
              <div className="glass-card rounded-xl p-6 relative group">
                <div className="mb-6">
                  <h3 className="font-headline-md text-headline-md text-on-surface">Language Distribution</h3>
                  <p className="font-body-sm text-body-sm text-on-surface-variant">By total lines generated</p>
                </div>
                <div className="flex flex-col gap-5 h-[300px] justify-center">
                  {LANG_DIST.map((lang) => (
                    <BarItem key={lang.language} {...lang} />
                  ))}
                </div>
              </div>
            </div>
          </div>
        </main>
    </>
  )
}
