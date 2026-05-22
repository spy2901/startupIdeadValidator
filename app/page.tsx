"use client";

import {
  FormEvent,
  useCallback,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import {
  analyzeStartup,
  getScoreLabel,
  mapApiResponse,
  type Results,
} from "@/lib/api";

const TERMINAL_LINES = [
  "Analyzing market...",
  "Generating ICP...",
  "Creating outreach strategy...",
] as const;

const LINE_DELAY_MS = 1100;
const FINISH_DELAY_MS = 500;

function terminalMinMs() {
  return TERMINAL_LINES.length * LINE_DELAY_MS + FINISH_DELAY_MS;
}

function TerminalLoader({ activeLine }: { activeLine: number }) {
  return (
    <div
      className="font-mono rounded-xl border border-emerald-500/20 bg-black/70 p-5 text-sm shadow-[0_0_40px_rgba(34,211,165,0.08)]"
      role="status"
      aria-live="polite"
      aria-label="Validation in progress"
    >
      <div className="mb-4 flex items-center gap-2 text-[var(--muted)]">
        <span className="h-2.5 w-2.5 rounded-full bg-red-500/90" />
        <span className="h-2.5 w-2.5 rounded-full bg-amber-500/90" />
        <span className="h-2.5 w-2.5 rounded-full bg-emerald-500/90" />
        <span className="ml-2 text-xs tracking-wide">agent — validate</span>
      </div>
      <div className="space-y-2.5">
        {TERMINAL_LINES.map((line, i) => {
          const visible = i <= activeLine;
          const isCurrent = i === activeLine;
          return (
            <p
              key={line}
              className={`flex items-center gap-1 transition-all duration-500 ${
                visible
                  ? "translate-y-0 opacity-100"
                  : "translate-y-1 opacity-0"
              }`}
            >
              <span className="text-emerald-400/80">&gt;</span>
              <span
                className={
                  isCurrent ? "text-emerald-300" : "text-[var(--muted)]"
                }
              >
                {line}
              </span>
              {isCurrent && (
                <span
                  className="ml-0.5 inline-block h-4 w-2 animate-terminal-blink bg-emerald-400 align-middle"
                  aria-hidden
                />
              )}
            </p>
          );
        })}
      </div>
    </div>
  );
}

function ResultCard({
  title,
  children,
  delay,
  badge,
}: {
  title: string;
  children: ReactNode;
  delay: number;
  badge?: string;
}) {
  return (
    <article
      className="animate-fade-up flex flex-col rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6 opacity-0 shadow-lg"
      style={{ animationDelay: `${delay}ms`, animationFillMode: "forwards" }}
    >
      <div className="mb-4 flex items-start justify-between gap-3">
        <h3 className="text-lg font-semibold tracking-tight text-[var(--text)]">
          {title}
        </h3>
        {badge && (
          <span className="shrink-0 rounded-full bg-[var(--accent-dim)] px-3 py-1 text-xs font-medium text-[var(--accent)]">
            {badge}
          </span>
        )}
      </div>
      <div className="flex-1 text-sm leading-relaxed text-[var(--muted)]">
        {children}
      </div>
    </article>
  );
}

export default function Home() {
  const [idea, setIdea] = useState("");
  const [audience, setAudience] = useState("");
  const [loading, setLoading] = useState(false);
  const [activeLine, setActiveLine] = useState(-1);
  const [results, setResults] = useState<Results | null>(null);
  const [badge, setBadge] = useState<string | undefined>();
  const [error, setError] = useState<string | null>(null);
  const resultsRef = useRef<HTMLElement>(null);
  const runIdRef = useRef(0);

  const runTerminal = useCallback(() => {
    setActiveLine(0);
    let line = 0;
    const tick = () => {
      if (line < TERMINAL_LINES.length - 1) {
        line += 1;
        setActiveLine(line);
        window.setTimeout(tick, LINE_DELAY_MS);
      }
    };
    window.setTimeout(tick, LINE_DELAY_MS);
  }, []);

  useEffect(() => {
    if (!loading) return;

    runTerminal();
    const runId = ++runIdRef.current;
    let terminalDone = false;
    let apiDone = false;
    let pendingResults: Results | null = null;
    let pendingBadge: string | undefined;
    let pendingError: string | null = null;

    const tryComplete = () => {
      if (runId !== runIdRef.current || !terminalDone || !apiDone) return;
      setLoading(false);
      setActiveLine(-1);
      setError(pendingError);
      setResults(pendingResults);
      setBadge(pendingBadge);
    };

    const terminalTimer = window.setTimeout(() => {
      terminalDone = true;
      tryComplete();
    }, terminalMinMs());

    analyzeStartup(idea, audience)
      .then((data) => {
        if (runId !== runIdRef.current) return;
        const mapped = mapApiResponse(data);
        pendingResults = mapped;
        pendingError = null;
        pendingBadge = getScoreLabel(
          mapped.score,
          data.decision?.verdict ?? data.analysis?.decision?.verdict
        );
        if (mapped.incomplete) {
          pendingError =
            "API returned a partial analysis (ICP only). Wait ~60s and try again, or check the backend returns decision, reddit_posts, and mvp_direction.";
        }
        apiDone = true;
        tryComplete();
      })
      .catch((err: Error) => {
        if (runId !== runIdRef.current) return;
        pendingError =
          err.message?.includes("Failed to fetch")
            ? "Could not reach the API. Is ngrok running?"
            : err.message || "Analysis failed.";
        pendingResults = null;
        pendingBadge = undefined;
        apiDone = true;
        tryComplete();
      });

    return () => {
      window.clearTimeout(terminalTimer);
      runIdRef.current += 1;
    };
  }, [loading, idea, audience, runTerminal]);

  useEffect(() => {
    if (results && !loading) {
      resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [results, loading]);

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (loading) return;
    setResults(null);
    setError(null);
    setBadge(undefined);
    setLoading(true);
    setActiveLine(0);
  }

  const scoreLabel =
    results && badge ? badge : results ? getScoreLabel(results.score) : undefined;

  return (
    <main className="relative z-10 mx-auto max-w-6xl px-6 pb-24 pt-16 md:px-10 md:pt-24">
      <section className="mb-16 text-center md:mb-20">
        <h1 className="text-balance text-4xl font-bold tracking-tight text-[var(--text)] md:text-5xl lg:text-6xl">
          Startup Idea Agent
        </h1>
        <p className="mx-auto mt-5 max-w-2xl text-lg text-[var(--muted)] md:text-xl">
          You bring the hypothesis. The agent runs the experiment.
        </p>
      </section>

      <section className="mb-12">
        {error && (
          <p
            role="alert"
            className="mx-auto mb-4 max-w-xl rounded-lg border border-red-500/40 bg-red-950/40 px-4 py-3 text-sm text-red-200"
          >
            {error}
          </p>
        )}

        <form
          onSubmit={handleSubmit}
          className="mx-auto max-w-xl space-y-5 rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-xl md:p-8"
        >
          <div>
            <label
              htmlFor="startup-idea"
              className="mb-2 block text-sm font-medium text-[var(--text)]"
            >
              Startup idea
            </label>
            <input
              id="startup-idea"
              name="idea"
              type="text"
              required
              placeholder="e.g. AI copilot for B2B sales outreach"
              value={idea}
              onChange={(e) => setIdea(e.target.value)}
              disabled={loading}
              className="w-full rounded-lg border border-[var(--border)] bg-black/30 px-4 py-3 text-[var(--text)] placeholder:text-[var(--muted)]/60 outline-none transition focus:border-[var(--accent)] focus:ring-1 focus:ring-[var(--accent)] disabled:opacity-60"
            />
          </div>
          <div>
            <label
              htmlFor="target-audience"
              className="mb-2 block text-sm font-medium text-[var(--text)]"
            >
              Target audience
            </label>
            <input
              id="target-audience"
              name="audience"
              type="text"
              required
              placeholder="e.g. VP Sales at SaaS startups"
              value={audience}
              onChange={(e) => setAudience(e.target.value)}
              disabled={loading}
              className="w-full rounded-lg border border-[var(--border)] bg-black/30 px-4 py-3 text-[var(--text)] placeholder:text-[var(--muted)]/60 outline-none transition focus:border-[var(--accent)] focus:ring-1 focus:ring-[var(--accent)] disabled:opacity-60"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-[var(--accent)] py-3.5 text-sm font-semibold text-[var(--bg)] transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-70"
          >
            {loading ? "Validating…" : "Validate Startup"}
          </button>
        </form>

        {loading && (
          <div className="mx-auto mt-8 max-w-xl animate-fade-up opacity-100">
            <TerminalLoader activeLine={activeLine} />
          </div>
        )}
      </section>

      {results && !loading && (
        <section ref={resultsRef} className="scroll-mt-8">
          <div className="grid gap-6 md:grid-cols-2">
            <ResultCard title="ICP" delay={0}>
              <p className="whitespace-pre-wrap">{results.icp}</p>
            </ResultCard>
            <ResultCard
              title="Validation Score"
              delay={100}
              badge={scoreLabel}
            >
              <div className="flex flex-col items-center justify-center py-4">
                <span className="text-5xl font-bold tabular-nums text-[var(--accent)]">
                  {results.score}
                </span>
                <span className="mt-1 text-xs uppercase tracking-wider text-[var(--muted)]">
                  / 100
                </span>
                <div className="mt-6 h-2 w-full overflow-hidden rounded-full bg-black/40">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-[var(--accent-dim)] to-[var(--accent)] transition-all duration-700"
                    style={{ width: `${results.score}%` }}
                  />
                </div>
              </div>
            </ResultCard>
            <ResultCard title="Outreach Message" delay={200}>
              <p className="whitespace-pre-wrap font-mono text-xs leading-relaxed text-[var(--text)]/90">
                {results.outreach}
              </p>
            </ResultCard>
            <ResultCard title="Landing Page Copy" delay={300}>
              <p className="whitespace-pre-wrap">{results.landing}</p>
            </ResultCard>
          </div>
        </section>
      )}
    </main>
  );
}
