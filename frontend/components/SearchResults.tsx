"use client";

interface SearchResult {
  content: string;
  metadata: Record<string, any>;
  score?: number;
}

interface SearchResultsProps {
  results: SearchResult[];
  loading: boolean;
}

export default function SearchResults({ results, loading }: SearchResultsProps) {
  if (loading) {
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            style={{
              backgroundColor: "rgba(255, 255, 255, 0.15)",
              backdropFilter: "blur(20px)",
              borderRadius: "20px",
              padding: "1.75rem",
              border: "1px solid rgba(255, 255, 255, 0.2)",
              boxShadow: "0 8px 32px rgba(0, 0, 0, 0.1)",
              animation: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
            }}
          >
            <div
              style={{
                height: "1.25rem",
                width: "60%",
                borderRadius: "10px",
                backgroundColor: "rgba(255, 255, 255, 0.2)",
                marginBottom: "1rem",
              }}
            />
            <div
              style={{
                height: "0.875rem",
                width: "100%",
                borderRadius: "8px",
                backgroundColor: "rgba(255, 255, 255, 0.2)",
                marginBottom: "0.75rem",
              }}
            />
            <div
              style={{
                height: "0.875rem",
                width: "85%",
                borderRadius: "8px",
                backgroundColor: "rgba(255, 255, 255, 0.2)",
              }}
            />
          </div>
        ))}
      </div>
    );
  }

  if (results.length === 0) {
    return null;
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
      {results.map((result, index) => (
        <div
          key={index}
          style={{
            backgroundColor: "rgba(255, 255, 255, 0.15)",
            backdropFilter: "blur(20px)",
            borderRadius: "20px",
            padding: "1.75rem",
            border: "1px solid rgba(255, 255, 255, 0.2)",
            boxShadow: "0 8px 32px rgba(0, 0, 0, 0.1)",
            transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
            cursor: "pointer",
            position: "relative",
            overflow: "hidden",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.boxShadow = "0 16px 48px rgba(0, 0, 0, 0.2)";
            e.currentTarget.style.transform = "translateY(-4px)";
            e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.4)";
            e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.2)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.boxShadow = "0 8px 32px rgba(0, 0, 0, 0.1)";
            e.currentTarget.style.transform = "translateY(0)";
            e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.2)";
            e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.15)";
          }}
        >
          {/* 배경 그라데이션 효과 */}
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              right: 0,
              height: "4px",
              background: `linear-gradient(90deg,
                rgba(232, 213, 255, 0.8) 0%,
                rgba(255, 213, 229, 0.8) 25%,
                rgba(213, 240, 255, 0.8) 50%,
                rgba(229, 255, 240, 0.8) 75%,
                rgba(255, 240, 229, 0.8) 100%)`,
              borderRadius: "20px 20px 0 0",
            }}
          />

          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              marginBottom: "1.25rem",
              marginTop: "0.25rem",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "0.875rem" }}>
              <div
                style={{
                  width: "40px",
                  height: "40px",
                  borderRadius: "12px",
                  background: "linear-gradient(135deg, rgba(255, 255, 255, 0.5) 0%, rgba(255, 255, 255, 0.4) 100%)",
                  color: "#1d1d1f",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "1rem",
                  fontWeight: 700,
                  fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Helvetica Neue', Helvetica, Arial, sans-serif",
                  border: "1px solid rgba(255, 255, 255, 0.5)",
                  boxShadow: "0 4px 12px rgba(0, 0, 0, 0.1)",
                }}
              >
                {index + 1}
              </div>
              {result.score !== undefined && (
                <div
                  style={{
                    fontSize: "0.8125rem",
                    color: "#1d1d1f",
                    fontWeight: 600,
                    padding: "0.375rem 0.875rem",
                    borderRadius: "10px",
                    backgroundColor: "rgba(255, 255, 255, 0.4)",
                    border: "1px solid rgba(255, 255, 255, 0.5)",
                  }}
                >
                  유사도: {(result.score * 100).toFixed(1)}%
                </div>
              )}
            </div>
            <div
              style={{
                padding: "0.375rem 0.75rem",
                borderRadius: "8px",
                backgroundColor: "rgba(255, 255, 255, 0.3)",
                fontSize: "0.75rem",
                color: "rgba(29, 29, 31, 0.8)",
                fontWeight: 500,
              }}
            >
              #{index + 1} 결과
            </div>
          </div>
          <p
            style={{
              color: "#1d1d1f",
              fontSize: "1.0625rem",
              lineHeight: "1.7",
              marginBottom: "1.25rem",
              fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Helvetica Neue', Helvetica, Arial, sans-serif",
              fontWeight: 400,
              letterSpacing: "-0.01em",
            }}
          >
            {result.content}
          </p>
          {result.metadata && Object.keys(result.metadata).length > 0 && (
            <div
              style={{
                display: "flex",
                flexWrap: "wrap",
                gap: "0.625rem",
                paddingTop: "1.25rem",
                borderTop: "1px solid rgba(255, 255, 255, 0.2)",
              }}
            >
              {Object.entries(result.metadata).map(([key, value]) => (
                <span
                  key={key}
                  style={{
                    fontSize: "0.8125rem",
                    padding: "0.5rem 0.875rem",
                    borderRadius: "10px",
                    backgroundColor: "rgba(255, 255, 255, 0.3)",
                    border: "1px solid rgba(255, 255, 255, 0.4)",
                    color: "#1d1d1f",
                    fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Helvetica Neue', Helvetica, Arial, sans-serif",
                    fontWeight: 500,
                    display: "flex",
                    alignItems: "center",
                    gap: "0.5rem",
                  }}
                >
                  <span style={{ opacity: 0.8 }}>{key}:</span>
                  <span style={{ fontWeight: 600 }}>{String(value)}</span>
                </span>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
