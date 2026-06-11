import { useMemo, useState } from "react";
import { useQuery } from "convex/react";
import { api } from "../../../convex/_generated/api";
import { Id } from "../../../convex/_generated/dataModel";

type DashboardTab = "tree" | "papers" | "claims" | "events";

interface DashboardShellProps {
  onOpenSessionGraph: (id: Id<"sessions">) => void;
}

interface SessionSummary {
  _id: Id<"sessions">;
  initialQuery: string;
  status: string;
  createdAt: number;
  updatedAt: number;
}

const projectStats = [
  { label: "Sessions", value: "3", tone: "text-sky-300" },
  { label: "Papers", value: "128", tone: "text-emerald-300" },
  { label: "Claims", value: "412", tone: "text-amber-300" },
  { label: "Gaps", value: "9", tone: "text-rose-300" },
];

const branchRows = [
  {
    label: "Root landscape scan",
    status: "running",
    papers: 34,
    rationale: "Broad coverage for methods, datasets, and recent surveys.",
  },
  {
    label: "Foundational methods",
    status: "completed",
    papers: 42,
    rationale: "Trace high-impact methods and citation ancestors.",
  },
  {
    label: "Weak evidence clusters",
    status: "pending",
    papers: 12,
    rationale: "Separate claims that need full-text verification.",
  },
];

const paperRows = [
  {
    title: "Survey of Evidence-Grounded Literature Exploration",
    year: "2025",
    status: "validated",
    claims: 18,
  },
  {
    title: "Citation Graphs for Research Navigation",
    year: "2024",
    status: "partial",
    claims: 11,
  },
  {
    title: "Claim Verification in Scientific Summaries",
    year: "2023",
    status: "needs review",
    claims: 23,
  },
];

const claimRows = [
  {
    claim: "Branch-level synthesis should preserve source provenance.",
    status: "supported",
    source: "Survey of Evidence-Grounded Literature Exploration",
  },
  {
    claim: "Citation count alone is insufficient for paper selection.",
    status: "supported",
    source: "Citation Graphs for Research Navigation",
  },
  {
    claim: "The current session has weak coverage of contradiction detection.",
    status: "needs review",
    source: "Session reflection",
  },
];

const eventRows = [
  { time: "09:12", event: "session_created", detail: "Research session shell initialized." },
  { time: "09:14", event: "branch_created", detail: "Root landscape branch queued." },
  { time: "09:21", event: "papers_found", detail: "34 candidate papers added." },
  { time: "09:33", event: "summary_validated", detail: "12 summaries passed groundedness checks." },
];

function statusClass(status: string): string {
  if (status === "running" || status === "validated" || status === "supported") {
    return "border-emerald-500/40 bg-emerald-950/40 text-emerald-200";
  }
  if (status === "completed") {
    return "border-sky-500/40 bg-sky-950/40 text-sky-200";
  }
  if (status === "partial" || status === "needs review") {
    return "border-amber-500/40 bg-amber-950/40 text-amber-200";
  }
  return "border-zinc-600 bg-zinc-800 text-zinc-300";
}

function formatDate(timestamp?: number): string {
  if (!timestamp) return "Not started";
  return new Date(timestamp).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function DashboardShell({ onOpenSessionGraph }: DashboardShellProps) {
  const sessions = useQuery(api.sessions.list);
  const [activeTab, setActiveTab] = useState<DashboardTab>("tree");
  const [query, setQuery] = useState("");

  const latestSession = useMemo(() => {
    if (!sessions || sessions.length === 0) return null;
    return [...sessions].sort((a, b) => b.createdAt - a.createdAt)[0];
  }, [sessions]);

  const sessionCount = sessions?.length ?? 0;

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      <div className="grid min-h-screen grid-cols-1 lg:grid-cols-[260px_minmax(0,1fr)]">
        <aside className="border-b border-zinc-800 bg-zinc-950 lg:border-b-0 lg:border-r">
          <div className="flex h-14 items-center border-b border-zinc-800 px-4">
            <div>
              <p className="text-sm font-semibold tracking-wide text-zinc-100">
                ERLA
              </p>
              <p className="text-xs text-zinc-500">Research mission control</p>
            </div>
          </div>

          <nav className="grid grid-cols-2 gap-1 px-3 py-4 sm:grid-cols-3 lg:block lg:space-y-1">
            {["Projects", "Sessions", "Scout Tree", "Papers", "Claims", "Settings"].map(
              (item, index) => (
                <button
                  key={item}
                  className={`flex h-9 w-full items-center justify-between rounded-md px-3 text-left text-sm transition ${
                    index === 0
                      ? "bg-zinc-800 text-white"
                      : "text-zinc-400 hover:bg-zinc-900 hover:text-zinc-100"
                  }`}
                >
                  <span>{item}</span>
                  {item === "Sessions" && (
                    <span className="rounded border border-zinc-700 px-1.5 text-xs text-zinc-400">
                      {sessionCount}
                    </span>
                  )}
                </button>
              )
            )}
          </nav>

          <div className="mx-3 border-t border-zinc-800 pt-4">
            <p className="px-3 text-xs font-medium uppercase text-zinc-500">
              Active Project
            </p>
            <div className="mt-3 rounded-md border border-zinc-800 bg-zinc-900 p-3">
              <p className="text-sm font-medium text-zinc-100">
                Evidence-grounded discovery
              </p>
              <p className="mt-1 text-xs leading-5 text-zinc-500">
                Literature map, branch state, and validation surfaces.
              </p>
            </div>
          </div>
        </aside>

        <main className="flex min-w-0 flex-col">
          <header className="flex min-h-14 flex-col gap-3 border-b border-zinc-800 bg-zinc-950 px-5 py-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="min-w-0">
              <p className="text-sm font-medium text-zinc-100">
                Project Dashboard
              </p>
              <p className="truncate text-xs text-zinc-500">
                Evidence-grounded discovery / {latestSession?.initialQuery ?? "new session"}
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <button className="h-8 rounded-md border border-zinc-700 px-3 text-sm text-zinc-300 hover:border-zinc-500">
                Export
              </button>
              <button className="h-8 rounded-md border border-emerald-700 bg-emerald-950 px-3 text-sm text-emerald-100 hover:border-emerald-500">
                Start
              </button>
              <button className="h-8 rounded-md border border-zinc-700 px-3 text-sm text-zinc-300 hover:border-zinc-500">
                Pause
              </button>
              <button className="h-8 rounded-md border border-zinc-700 px-3 text-sm text-zinc-300 hover:border-zinc-500">
                Cancel
              </button>
            </div>
          </header>

          <section className="grid min-h-0 flex-1 grid-cols-1 lg:grid-cols-[minmax(0,1fr)_340px]">
            <div className="min-w-0 overflow-y-auto">
              <div className="border-b border-zinc-800 px-5 py-4">
                <div className="grid gap-3 lg:grid-cols-[minmax(0,1fr)_220px]">
                  <label className="block">
                    <span className="mb-1 block text-xs font-medium uppercase text-zinc-500">
                      Start Session
                    </span>
                    <input
                      value={query}
                      onChange={(event) => setQuery(event.target.value)}
                      placeholder="Map transformer interpretability evidence gaps"
                      className="h-10 w-full rounded-md border border-zinc-700 bg-zinc-900 px-3 text-sm text-zinc-100 outline-none focus:border-sky-500"
                    />
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    <button className="mt-5 h-10 rounded-md border border-sky-700 bg-sky-950 px-3 text-sm text-sky-100 hover:border-sky-500">
                      Queue
                    </button>
                    <button className="mt-5 h-10 rounded-md border border-zinc-700 px-3 text-sm text-zinc-300 hover:border-zinc-500">
                      Settings
                    </button>
                  </div>
                </div>
              </div>

              <div className="grid gap-3 border-b border-zinc-800 p-5 sm:grid-cols-2 xl:grid-cols-4">
                {projectStats.map((stat) => (
                  <div
                    key={stat.label}
                    className="rounded-md border border-zinc-800 bg-zinc-900 p-3"
                  >
                    <p className={`text-2xl font-semibold ${stat.tone}`}>
                      {stat.value}
                    </p>
                    <p className="text-xs uppercase text-zinc-500">{stat.label}</p>
                  </div>
                ))}
              </div>

              <div className="border-b border-zinc-800 px-5">
                <div className="flex flex-wrap gap-1 py-3">
                  {[
                    ["tree", "Scout Tree"],
                    ["papers", "Papers"],
                    ["claims", "Claims"],
                    ["events", "Events"],
                  ].map(([value, label]) => (
                    <button
                      key={value}
                      onClick={() => setActiveTab(value as DashboardTab)}
                      className={`h-8 rounded-md px-3 text-sm ${
                        activeTab === value
                          ? "bg-zinc-800 text-white"
                          : "text-zinc-400 hover:bg-zinc-900 hover:text-zinc-100"
                      }`}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="p-5">
                {renderCenterPanel(activeTab, latestSession, onOpenSessionGraph)}
              </div>
            </div>

            <aside className="border-t border-zinc-800 bg-zinc-950 lg:border-l lg:border-t-0">
              <div className="border-b border-zinc-800 p-4">
                <p className="text-sm font-medium text-zinc-100">Inspector</p>
                <p className="mt-1 text-xs text-zinc-500">
                  Selected branch, paper, claim, or hypothesis.
                </p>
              </div>

              <div className="space-y-4 p-4">
                <div>
                  <p className="text-xs font-medium uppercase text-zinc-500">
                    Session
                  </p>
                  <p className="mt-2 text-sm font-medium text-zinc-100">
                    {latestSession?.initialQuery ?? "No replay session selected"}
                  </p>
                  <dl className="mt-3 grid grid-cols-2 gap-2 text-xs">
                    <div className="rounded-md border border-zinc-800 bg-zinc-900 p-2">
                      <dt className="text-zinc-500">Status</dt>
                      <dd className="mt-1 capitalize text-zinc-200">
                        {latestSession?.status ?? "pending"}
                      </dd>
                    </div>
                    <div className="rounded-md border border-zinc-800 bg-zinc-900 p-2">
                      <dt className="text-zinc-500">Updated</dt>
                      <dd className="mt-1 text-zinc-200">
                        {formatDate(latestSession?.updatedAt)}
                      </dd>
                    </div>
                  </dl>
                </div>

                <div>
                  <p className="text-xs font-medium uppercase text-zinc-500">
                    Validation Trace
                  </p>
                  <div className="mt-2 space-y-2">
                    {["Summary groundedness", "Claim extraction", "Evidence ledger"].map(
                      (item, index) => (
                        <div
                          key={item}
                          className="flex items-center justify-between rounded-md border border-zinc-800 bg-zinc-900 px-3 py-2 text-xs"
                        >
                          <span className="text-zinc-300">{item}</span>
                          <span className={index === 0 ? "text-emerald-300" : "text-zinc-500"}>
                            {index === 0 ? "ready" : "queued"}
                          </span>
                        </div>
                      )
                    )}
                  </div>
                </div>
              </div>
            </aside>
          </section>

          <footer className="grid min-h-44 grid-cols-1 border-t border-zinc-800 bg-zinc-950 lg:h-44 lg:grid-cols-[minmax(0,1fr)_340px]">
            <div className="overflow-y-auto p-4">
              <div className="mb-3 flex items-center justify-between">
                <p className="text-sm font-medium text-zinc-100">Event Log</p>
                <span className="text-xs text-zinc-500">{eventRows.length} events</span>
              </div>
              <div className="grid gap-2 md:grid-cols-2">
                {eventRows.map((event) => (
                  <div
                    key={`${event.time}-${event.event}`}
                    className="rounded-md border border-zinc-800 bg-zinc-900 px-3 py-2"
                  >
                    <div className="flex items-center justify-between gap-3">
                      <span className="text-xs text-zinc-500">{event.time}</span>
                      <span className="text-xs text-sky-300">{event.event}</span>
                    </div>
                    <p className="mt-1 text-sm text-zinc-300">{event.detail}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="border-t border-zinc-800 p-4 lg:border-l lg:border-t-0">
              <p className="text-sm font-medium text-zinc-100">Jobs</p>
              <div className="mt-3 space-y-2">
                {["paper_search", "summary_validation", "claim_extraction"].map(
                  (job, index) => (
                    <div key={job}>
                      <div className="mb-1 flex justify-between text-xs">
                        <span className="text-zinc-400">{job}</span>
                        <span className="text-zinc-500">{index === 0 ? "68%" : "0%"}</span>
                      </div>
                      <div className="h-1.5 rounded bg-zinc-800">
                        <div
                          className="h-1.5 rounded bg-emerald-500"
                          style={{ width: index === 0 ? "68%" : "0%" }}
                        />
                      </div>
                    </div>
                  )
                )}
              </div>
            </div>
          </footer>
        </main>
      </div>
    </div>
  );
}

function renderCenterPanel(
  activeTab: DashboardTab,
  latestSession: SessionSummary | null,
  onOpenSessionGraph: (id: Id<"sessions">) => void
) {
  if (activeTab === "tree") {
    return (
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-zinc-100">Scout Tree</p>
            <p className="text-xs text-zinc-500">Branch state and selection rationale.</p>
          </div>
          {latestSession && (
            <button
              onClick={() => onOpenSessionGraph(latestSession._id)}
              className="h-8 rounded-md border border-sky-700 px-3 text-sm text-sky-100 hover:border-sky-500"
            >
              Open Graph
            </button>
          )}
        </div>
        <div className="grid gap-3 lg:grid-cols-3">
          {branchRows.map((branch) => (
            <div
              key={branch.label}
              className="min-h-40 rounded-md border border-zinc-800 bg-zinc-900 p-4"
            >
              <div className="flex items-start justify-between gap-3">
                <p className="text-sm font-medium text-zinc-100">{branch.label}</p>
                <span className={`rounded border px-2 py-0.5 text-xs ${statusClass(branch.status)}`}>
                  {branch.status}
                </span>
              </div>
              <p className="mt-3 text-xs leading-5 text-zinc-500">{branch.rationale}</p>
              <p className="mt-4 text-xs text-zinc-400">{branch.papers} papers</p>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (activeTab === "papers") {
    return (
      <div className="overflow-hidden rounded-md border border-zinc-800">
        {paperRows.map((paper) => (
          <div
            key={paper.title}
            className="grid grid-cols-1 gap-2 border-b border-zinc-800 bg-zinc-900 px-4 py-3 last:border-b-0 sm:grid-cols-[minmax(0,1fr)_90px_120px_90px] sm:items-center sm:gap-3"
          >
            <p className="truncate text-sm text-zinc-100">{paper.title}</p>
            <p className="text-sm text-zinc-400">{paper.year}</p>
            <span className={`w-fit rounded border px-2 py-0.5 text-xs ${statusClass(paper.status)}`}>
              {paper.status}
            </span>
            <p className="text-sm text-zinc-400 sm:text-right">{paper.claims} claims</p>
          </div>
        ))}
      </div>
    );
  }

  if (activeTab === "claims") {
    return (
      <div className="space-y-2">
        {claimRows.map((claim) => (
          <div
            key={claim.claim}
            className="rounded-md border border-zinc-800 bg-zinc-900 p-4"
          >
            <div className="flex items-start justify-between gap-4">
              <p className="text-sm text-zinc-100">{claim.claim}</p>
              <span className={`shrink-0 rounded border px-2 py-0.5 text-xs ${statusClass(claim.status)}`}>
                {claim.status}
              </span>
            </div>
            <p className="mt-2 text-xs text-zinc-500">{claim.source}</p>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {eventRows.map((event) => (
        <div
          key={`${event.time}-${event.event}`}
          className="grid grid-cols-1 gap-2 rounded-md border border-zinc-800 bg-zinc-900 px-4 py-3 sm:grid-cols-[64px_180px_minmax(0,1fr)] sm:gap-3"
        >
          <span className="text-sm text-zinc-500">{event.time}</span>
          <span className="text-sm text-sky-300">{event.event}</span>
          <span className="text-sm text-zinc-300">{event.detail}</span>
        </div>
      ))}
    </div>
  );
}
