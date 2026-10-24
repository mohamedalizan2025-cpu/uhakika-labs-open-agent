import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, afterEach, describe, expect, it, vi } from "vitest";

import App from "@/App";

// --- Helper: render with QueryClientProvider ---
function renderWithProviders(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

// --- Mock the global fetch to control API responses ---

const HEALTH_SAMPLE = {
  ok: true,
  default_mode: "sample" as const,
  sample_ready: true,
  live_ready: false,
  integrations: {
    zetaris: { status: "sample_only", missing: ["ZETARIS_REST_URL", "ZETARIS_ORG_ID", "ZETARIS_API_KEY"] },
    nightshift: { status: "not_configured", missing: ["METERLESS_BASE_URL", "METERLESS_RUNTIME_TOKEN", "METERLESS_MODEL"] },
  },
  missing_env_names: ["METERLESS_BASE_URL", "METERLESS_RUNTIME_TOKEN", "METERLESS_MODEL", "ZETARIS_REST_URL", "ZETARIS_ORG_ID", "ZETARIS_API_KEY"],
};

const HEALTH_LIVE_READY = {
  ...HEALTH_SAMPLE,
  default_mode: "live" as const,
  live_ready: true,
  integrations: {
    zetaris: { status: "live_ready", missing: [] },
    nightshift: { status: "live_ready", missing: [] },
  },
  missing_env_names: [],
};

const RUN_RESPONSE = {
  case_id: "CASE-INV-004",
  revenue_at_risk: 126_000_000,
  supported_cause: "Required compliance / tax evidence missing",
  blocker_class: "execution_documentation" as const,
  rejected_hypotheses: [
    { id: "H1" as const, reason: "delivery confirmed" },
    { id: "H2" as const, reason: "acceptance not the issue" },
    { id: "H3" as const, reason: "invoice is correct" },
  ],
  evidence: [
    { evidence_id: "CMP-005", source: "compliance_items", summary: "Tax clearance required but not submitted" },
    { evidence_id: "INV-004", source: "invoices", summary: "TZS 126,000,000 pending" },
  ],
  recommendation: "Submit tax clearance certificate",
  approval_status: "pending" as const,
  trace: [{ ts: "2026-01-01T00:00:00Z", agent: "Router", action: "route", tool: null, source_result_summary: null, decision: "fallback", confidence: null, retry_count: 0, model_route: null, evidence_ids: [] }],
};

const INSUFFICIENT_RESPONSE = {
  ...RUN_RESPONSE,
  case_id: "CASE-INV-999",
  revenue_at_risk: 0,
  supported_cause: "insufficient_evidence",
  blocker_class: null,
  rejected_hypotheses: [],
  evidence: [],
  recommendation: "insufficient_evidence",
  approval_status: "not_required" as const,
};

let fetchCalls: { url: string; options?: RequestInit }[] = [];

function mockFetch(healthResponse: unknown = HEALTH_SAMPLE) {
  fetchCalls = [];
  vi.stubGlobal("fetch", vi.fn(async (url: string, options?: RequestInit) => {
    fetchCalls.push({ url, options });
    if (url === "/health") {
      return new Response(JSON.stringify(healthResponse), { status: 200, headers: { "Content-Type": "application/json" } });
    }
    if (url === "/run") {
      return new Response(JSON.stringify(RUN_RESPONSE), { status: 200, headers: { "Content-Type": "application/json" } });
    }
    return new Response("not found", { status: 404 });
  }));
}

function getRunCalls() {
  return fetchCalls.filter((c) => c.url === "/run");
}

function parseRunBody(call: { options?: RequestInit }) {
  return JSON.parse(call.options?.body as string);
}

// --- Tests ---

describe("App — default page load", () => {
  beforeEach(() => {
    vi.stubEnv("VITE_DEMO_AUTORUN", "false");
    mockFetch();
  });
  afterEach(() => { vi.unstubAllEnvs(); vi.unstubAllGlobals(); });

  it("does not POST /run on page load by default", async () => {
    renderWithProviders(<App />);
    // Wait for health to resolve
    await waitFor(() => expect(screen.getByText(/Run guided sample/i)).toBeInTheDocument());
    const runPosts = getRunCalls();
    expect(runPosts).toHaveLength(0);
  });

  it("shows the guided-demo button when no result exists", async () => {
    renderWithProviders(<App />);
    await waitFor(() => expect(screen.getByText(/Run guided sample/i)).toBeInTheDocument());
  });
});

describe("App — demo auto-run opt-in (VITE_DEMO_AUTORUN=true)", () => {
  beforeEach(() => {
    vi.stubEnv("VITE_DEMO_AUTORUN", "true");
    mockFetch();
  });
  afterEach(() => { vi.unstubAllEnvs(); vi.unstubAllGlobals(); });

  it("auto-runs INV-004 with sample_mode:true when enabled", async () => {
    renderWithProviders(<App />);
    await waitFor(() => {
      const posts = getRunCalls();
      expect(posts.length).toBeGreaterThanOrEqual(1);
    }, { timeout: 3000 });
    const body = parseRunBody(getRunCalls()[0]);
    expect(body.invoice_id).toBe("INV-004");
    expect(body.sample_mode).toBe(true);
  });

  it("auto-run NEVER sends sample_mode:false", async () => {
    renderWithProviders(<App />);
    await waitFor(() => {
      expect(getRunCalls().length).toBeGreaterThanOrEqual(1);
    }, { timeout: 3000 });
    for (const call of getRunCalls()) {
      expect(parseRunBody(call).sample_mode).toBe(true);
    }
  });
});

describe("App — sample chips", () => {
  beforeEach(() => {
    vi.stubEnv("VITE_DEMO_AUTORUN", "false");
    mockFetch();
  });
  afterEach(() => { vi.unstubAllEnvs(); vi.unstubAllGlobals(); });

  it("chip click sends correct question, invoice, sample_mode:true", async () => {
    const user = userEvent.setup();
    renderWithProviders(<App />);
    await waitFor(() => expect(screen.getByText(/Sample scenarios/i)).toBeInTheDocument());

    // Click INV-005 chip
    const chip = screen.getByRole("button", { name: "INV-005" });
    await user.click(chip);

    await waitFor(() => {
      const posts = getRunCalls();
      expect(posts.length).toBeGreaterThanOrEqual(1);
    });
    const body = parseRunBody(getRunCalls().at(-1)!);
    expect(body.invoice_id).toBe("INV-005");
    expect(body.sample_mode).toBe(true);
    expect(body.question).toContain("health-depot");
  });
});

describe("App — guided demo button", () => {
  beforeEach(() => {
    vi.stubEnv("VITE_DEMO_AUTORUN", "false");
    mockFetch();
  });
  afterEach(() => { vi.unstubAllEnvs(); vi.unstubAllGlobals(); });

  it("clicking 'Run guided sample investigation' sends INV-004 sample_mode:true", async () => {
    const user = userEvent.setup();
    renderWithProviders(<App />);
    await waitFor(() => expect(screen.getByText(/Run guided sample/i)).toBeInTheDocument());

    await user.click(screen.getByText(/Run guided sample/i));

    await waitFor(() => {
      expect(getRunCalls().length).toBeGreaterThanOrEqual(1);
    });
    const body = parseRunBody(getRunCalls()[0]);
    expect(body.invoice_id).toBe("INV-004");
    expect(body.sample_mode).toBe(true);
  });
});

describe("App — manual form submission", () => {
  beforeEach(() => {
    vi.stubEnv("VITE_DEMO_AUTORUN", "false");
    mockFetch();
  });
  afterEach(() => { vi.unstubAllEnvs(); vi.unstubAllGlobals(); });

  it("uses typed values not fixture conclusions", async () => {
    const user = userEvent.setup();
    renderWithProviders(<App />);
    await waitFor(() => expect(screen.getByLabelText(/Invoice ID/i)).toBeInTheDocument());

    // Clear and type custom invoice
    const invoiceInput = screen.getByLabelText(/Invoice ID/i);
    await user.clear(invoiceInput);
    await user.type(invoiceInput, "INV-CUSTOM");

    const questionArea = screen.getByLabelText(/Investigator question/i);
    await user.clear(questionArea);
    await user.type(questionArea, "Why is INV-CUSTOM unpaid?");

    await user.click(screen.getByRole("button", { name: /Run investigation/i }));

    await waitFor(() => {
      expect(getRunCalls().length).toBeGreaterThanOrEqual(1);
    });
    const body = parseRunBody(getRunCalls()[0]);
    expect(body.invoice_id).toBe("INV-CUSTOM");
    expect(body.question).toBe("Why is INV-CUSTOM unpaid?");
    expect(body.sample_mode).toBe(true);
  });
});

describe("App — Sample/Live mode selector", () => {
  afterEach(() => { vi.unstubAllEnvs(); vi.unstubAllGlobals(); });

  it("Live button is disabled when live_ready=false", async () => {
    vi.stubEnv("VITE_DEMO_AUTORUN", "false");
    mockFetch(HEALTH_SAMPLE);
    renderWithProviders(<App />);
    // Wait for health to resolve (status = online)
    await waitFor(() => expect(screen.getByText(/Service online/i)).toBeInTheDocument());
    const liveBtn = screen.getByText("Live").closest("button")!;
    expect(liveBtn).toBeDisabled();
  });

  it("Live button is enabled when live_ready=true and sends sample_mode:false", async () => {
    vi.stubEnv("VITE_DEMO_AUTORUN", "false");
    mockFetch(HEALTH_LIVE_READY);
    const user = userEvent.setup();
    renderWithProviders(<App />);
    // Wait for health to resolve
    await waitFor(() => expect(screen.getByText(/Service online/i)).toBeInTheDocument());

    const liveBtn = screen.getByText("Live").closest("button")!;
    expect(liveBtn).not.toBeDisabled();
    await user.click(liveBtn);

    // Now submit via form
    await user.click(screen.getByRole("button", { name: /Run investigation/i }));

    await waitFor(() => {
      expect(getRunCalls().length).toBeGreaterThanOrEqual(1);
    });
    const body = parseRunBody(getRunCalls()[0]);
    expect(body.sample_mode).toBe(false);
  });
});

describe("App — states", () => {
  afterEach(() => { vi.unstubAllEnvs(); vi.unstubAllGlobals(); });

  it("shows loading state after submitting", async () => {
    vi.stubEnv("VITE_DEMO_AUTORUN", "false");
    mockFetch();
    // Make /run slow
    let resolveRun: (v: Response) => void;
    const runPromise = new Promise<Response>((r) => { resolveRun = r; });
    vi.stubGlobal("fetch", vi.fn(async (url: string) => {
      fetchCalls.push({ url });
      if (url === "/health") {
        return new Response(JSON.stringify(HEALTH_SAMPLE), { status: 200, headers: { "Content-Type": "application/json" } });
      }
      if (url === "/run") return runPromise;
      return new Response("n/a", { status: 404 });
    }));

    const user = userEvent.setup();
    renderWithProviders(<App />);
    await waitFor(() => expect(screen.getByText(/Run guided sample/i)).toBeInTheDocument());

    // Start a run via guided demo
    await user.click(screen.getByText(/Run guided sample/i));

    // Loading state visible (stages show after mutation starts)
    await waitFor(() => expect(screen.getByText(/Routing intent/i)).toBeInTheDocument(), { timeout: 2000 });

    // Resolve the run
    resolveRun!(new Response(JSON.stringify(RUN_RESPONSE), { status: 200, headers: { "Content-Type": "application/json" } }));
    await waitFor(() => expect(screen.getAllByText(/TZS/).length).toBeGreaterThan(0));
  });

  it("shows offline state when backend unreachable", async () => {
    vi.stubEnv("VITE_DEMO_AUTORUN", "false");
    vi.stubGlobal("fetch", vi.fn(async () => { throw new TypeError("fetch failed"); }));
    renderWithProviders(<App />);
    await waitFor(() => expect(screen.getByText(/Service offline/i)).toBeInTheDocument());
  });

  it("shows error state when API returns non-200", async () => {
    vi.stubEnv("VITE_DEMO_AUTORUN", "false");
    vi.stubGlobal("fetch", vi.fn(async (url: string) => {
      if (url === "/health") {
        return new Response(JSON.stringify(HEALTH_SAMPLE), { status: 200, headers: { "Content-Type": "application/json" } });
      }
      return new Response(JSON.stringify({ detail: "service unavailable" }), { status: 503, headers: { "Content-Type": "application/json" } });
    }));

    const user = userEvent.setup();
    renderWithProviders(<App />);
    await waitFor(() => expect(screen.getByText(/Run guided sample/i)).toBeInTheDocument());
    await user.click(screen.getByText(/Run guided sample/i));
    await waitFor(() => expect(screen.getByText(/service unavailable/i)).toBeInTheDocument());
  });

  it("renders insufficient-evidence response", async () => {
    vi.stubEnv("VITE_DEMO_AUTORUN", "false");
    vi.stubGlobal("fetch", vi.fn(async (url: string) => {
      fetchCalls.push({ url });
      if (url === "/health") {
        return new Response(JSON.stringify(HEALTH_SAMPLE), { status: 200, headers: { "Content-Type": "application/json" } });
      }
      return new Response(JSON.stringify(INSUFFICIENT_RESPONSE), { status: 200, headers: { "Content-Type": "application/json" } });
    }));

    const user = userEvent.setup();
    renderWithProviders(<App />);
    await waitFor(() => expect(screen.getByText(/Run guided sample/i)).toBeInTheDocument());
    await user.click(screen.getByText(/Run guided sample/i));
    await waitFor(() => expect(screen.getAllByText(/Insufficient evidence/i).length).toBeGreaterThan(0));
  });
});

describe("Result cards render server values (no hardcoded conclusions)", () => {
  beforeEach(() => {
    vi.stubEnv("VITE_DEMO_AUTORUN", "false");
    mockFetch();
  });
  afterEach(() => { vi.unstubAllEnvs(); vi.unstubAllGlobals(); });

  it("displays revenue and cause from mocked API response", async () => {
    const user = userEvent.setup();
    renderWithProviders(<App />);
    await waitFor(() => expect(screen.getByText(/Run guided sample/i)).toBeInTheDocument());
    await user.click(screen.getByText(/Run guided sample/i));

    // Values come from the mocked response, not the component source
    await waitFor(() => expect(screen.getAllByText(/126,000,000/).length).toBeGreaterThan(0));
    expect(screen.getAllByText(/Required compliance/i).length).toBeGreaterThan(0);
  });
});
