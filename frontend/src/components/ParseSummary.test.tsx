// SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
// SPDX-License-Identifier: Apache-2.0

import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import type { ParseResult } from "../lib/api";
import { licenseCounts, ParseSummary } from "./ParseSummary";

type Pkg = ParseResult["document"]["packages"][number];

function pkg(name: string, expression: string | null): Pkg {
  return {
    name,
    version: "1",
    license_concluded: expression ? { raw: expression } : null,
    license_declared: null,
    copyright: null,
  };
}

function result(
  packages: Pkg[],
  licenses: string[],
  warnings: string[] = [],
): ParseResult {
  return {
    document: {
      name: "demo",
      packages,
      licenses: licenses.map((id) => ({ license_id: id, name: id })),
    },
    warnings,
  };
}

describe("licenseCounts", () => {
  it("counts a package towards every license its expression names", () => {
    const parsed = result(
      [pkg("a", "MIT"), pkg("b", "MIT OR Apache-2.0"), pkg("c", "Apache-2.0")],
      ["MIT", "Apache-2.0"],
    );
    expect(licenseCounts(parsed)).toEqual([
      { id: "Apache-2.0", count: 2 },
      { id: "MIT", count: 2 },
    ]);
  });

  it("matches whole identifiers, not fragments of longer ones", () => {
    // "GPL-2.0-only" contains "GPL-2.0" as a substring; a naive match would double-count.
    const parsed = result([pkg("a", "GPL-2.0-only")], ["GPL-2.0-only", "MIT"]);
    expect(licenseCounts(parsed)).toEqual([
      { id: "GPL-2.0-only", count: 1 },
      { id: "MIT", count: 0 },
    ]);
  });

  it("falls back to the declared expression when nothing was concluded", () => {
    const parsed = result([{ ...pkg("a", null), license_declared: { raw: "MIT" } }], ["MIT"]);
    expect(licenseCounts(parsed)).toEqual([{ id: "MIT", count: 1 }]);
  });

  it("orders by how many components use the license", () => {
    const parsed = result(
      [pkg("a", "MIT"), pkg("b", "MIT"), pkg("c", "BSD-3-Clause")],
      ["BSD-3-Clause", "MIT"],
    );
    expect(licenseCounts(parsed).map((entry) => entry.id)).toEqual(["MIT", "BSD-3-Clause"]);
  });
});

describe("ParseSummary", () => {
  it("shows the totals and the per-license breakdown", () => {
    render(<ParseSummary lang="en" parsed={result([pkg("a", "MIT")], ["MIT"])} />);
    expect(screen.getByText("demo")).toBeInTheDocument();
    expect(screen.getByText(/1 components, 1 licenses/)).toBeInTheDocument();
    expect(screen.getByText(/MIT/)).toBeInTheDocument();
  });

  it("says nothing about warnings when there are none", () => {
    render(<ParseSummary lang="en" parsed={result([pkg("a", "MIT")], ["MIT"])} />);
    expect(screen.queryByTestId("toggle-warnings")).not.toBeInTheDocument();
  });

  it("leaves an unrecognised warning as written, with no invented explanation", () => {
    const parsed = result([pkg("a", "MIT")], ["MIT"], ["something new from the backend"]);
    render(<ParseSummary lang="en" parsed={parsed} />);
    expect(screen.getByTestId("toggle-warnings")).toHaveTextContent("1 warning");
  });
});
