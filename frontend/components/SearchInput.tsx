"use client";

import { useState, FormEvent } from "react";

interface SearchInputProps {
  onSearch: (query: string) => void;
  loading: boolean;
}

export default function SearchInput({ onSearch, loading }: SearchInputProps) {
  const [inputValue, setInputValue] = useState("");
  const [isFocused, setIsFocused] = useState(false);

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (inputValue.trim() && !loading) {
      onSearch(inputValue.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ position: "relative", width: "100%" }}>
      <div
        style={{
          position: "relative",
          width: "100%",
          transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
        }}
      >
        <div
          style={{
            position: "absolute",
            left: "1.5rem",
            top: "50%",
            transform: "translateY(-50%)",
            display: "flex",
            alignItems: "center",
            pointerEvents: "none",
            zIndex: 1,
          }}
        >
          <svg
            width="22"
            height="22"
            viewBox="0 0 24 24"
            fill="none"
            stroke={isFocused ? "#1d1d1f" : "rgba(29, 29, 31, 0.6)"}
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            style={{
              transition: "all 0.2s ease",
            }}
          >
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.35-4.35" />
          </svg>
        </div>
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="검색어를 입력하세요..."
          disabled={loading}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          style={{
            width: "100%",
            border: `2px solid ${isFocused ? "rgba(255, 255, 255, 0.5)" : "rgba(255, 255, 255, 0.2)"}`,
            borderRadius: "18px",
            backgroundColor: "rgba(255, 255, 255, 0.4)",
            backdropFilter: "blur(20px)",
            color: "#1d1d1f",
            padding: "1.375rem 6rem 1.375rem 3.75rem",
            fontSize: "17px",
            fontWeight: 400,
            letterSpacing: "-0.01em",
            fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Helvetica Neue', Helvetica, Arial, sans-serif",
            boxShadow: isFocused
              ? "0 12px 40px rgba(0, 0, 0, 0.2), 0 0 0 4px rgba(255, 255, 255, 0.1)"
              : "0 4px 20px rgba(0, 0, 0, 0.1)",
            transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
            outline: "none",
            opacity: loading ? 0.6 : 1,
            WebkitFontSmoothing: "antialiased",
            MozOsxFontSmoothing: "grayscale",
          }}
        />
        <button
          type="submit"
          disabled={loading || !inputValue.trim()}
          style={{
            position: "absolute",
            right: "0.5rem",
            top: "50%",
            transform: "translateY(-50%)",
            background: inputValue.trim() && !loading
              ? "linear-gradient(135deg, rgba(255, 255, 255, 0.3) 0%, rgba(255, 255, 255, 0.2) 100%)"
              : "rgba(255, 255, 255, 0.1)",
            borderRadius: "14px",
            padding: "0.875rem 1.75rem",
            border: "1px solid rgba(255, 255, 255, 0.3)",
            cursor: loading || !inputValue.trim() ? "not-allowed" : "pointer",
            boxShadow: inputValue.trim() && !loading
              ? "0 6px 20px rgba(0, 0, 0, 0.2)"
              : "none",
            fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Helvetica Neue', Helvetica, Arial, sans-serif",
            color: "#1d1d1f",
            transition: "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "0.5rem",
            fontSize: "0.9375rem",
            fontWeight: 600,
            backdropFilter: "blur(10px)",
          }}
          onMouseEnter={(e) => {
            if (!e.currentTarget.disabled && inputValue.trim()) {
              e.currentTarget.style.background = "linear-gradient(135deg, rgba(255, 255, 255, 0.4) 0%, rgba(255, 255, 255, 0.3) 100%)";
              e.currentTarget.style.boxShadow = "0 8px 24px rgba(0, 0, 0, 0.3)";
              e.currentTarget.style.transform = "translateY(-50%) scale(1.05)";
            }
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = inputValue.trim()
              ? "linear-gradient(135deg, rgba(255, 255, 255, 0.3) 0%, rgba(255, 255, 255, 0.2) 100%)"
              : "rgba(255, 255, 255, 0.1)";
            e.currentTarget.style.boxShadow = inputValue.trim()
              ? "0 6px 20px rgba(0, 0, 0, 0.2)"
              : "none";
            e.currentTarget.style.transform = "translateY(-50%) scale(1)";
          }}
        >
          {loading ? (
            <>
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                style={{
                  animation: "spin 1s linear infinite",
                }}
              >
                <circle
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                  strokeOpacity="0.25"
                />
                <path
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  opacity="0.75"
                />
              </svg>
              검색 중...
            </>
          ) : (
            <>
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            </>
          )}
        </button>
      </div>
      <style jsx>{`
        @keyframes spin {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }
      `}</style>
    </form>
  );
}
