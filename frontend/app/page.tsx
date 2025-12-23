"use client";

import { useState, useEffect, useRef } from "react";
import SearchInput from "@/components/SearchInput";

interface Message {
  id: string;
  type: "user" | "assistant";
  content: string;
  timestamp: Date;
  results?: Array<{
    content: string;
    metadata: Record<string, any>;
    score?: number;
  }>;
}

type EndpointMode = "search" | "chat" | "rag";

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [endpointMode, setEndpointMode] = useState<EndpointMode>("rag");
  const [stats, setStats] = useState({
    totalSearches: 0,
    avgResults: 0,
    responseTime: 0,
    totalTokens: 0,
    estimatedCost: 0,
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 비용 추정 함수 (간단한 추정)
  const estimateCost = (query: string, answer?: string, sources?: any[]) => {
    // Embeddings 비용 (text-embedding-3-small: $0.02 / 1M tokens)
    const queryTokens = Math.ceil(query.length / 4); // 대략적인 토큰 수
    const embeddingCost = (queryTokens / 1_000_000) * 0.02;

    // LLM 비용 (gpt-4o-mini: $0.15 / 1M input, $0.60 / 1M output)
    let llmCost = 0;
    if (answer) {
      const inputTokens = queryTokens + (sources?.reduce((sum, s) => sum + Math.ceil(s.content.length / 4), 0) || 0);
      const outputTokens = Math.ceil(answer.length / 4);
      llmCost = (inputTokens / 1_000_000) * 0.15 + (outputTokens / 1_000_000) * 0.60;
    }

    return {
      tokens: queryTokens + (answer ? Math.ceil(answer.length / 4) : 0),
      cost: embeddingCost + llmCost,
    };
  };

  const handleSearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      return;
    }

    const startTime = Date.now();
    setLoading(true);
    setError(null);

    // 사용자 메시지 추가
    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: searchQuery,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);

    try {
      let endpoint = "";
      let requestBody: any = {};

      // 엔드포인트 모드에 따라 선택
      switch (endpointMode) {
        case "search":
          endpoint = "/search";
          requestBody = { query: searchQuery, k: 5 };
          break;
        case "chat":
          endpoint = "/chat";
          requestBody = { query: searchQuery };
          break;
        case "rag":
          endpoint = "/rag";
          requestBody = { query: searchQuery };
          break;
      }

      // 개발/프로덕션 환경 감지
      const isDevelopment = typeof window !== 'undefined' &&
        (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');

      // API URL 결정
      // Mixed Content 문제 방지: HTTPS 사이트에서는 HTTPS 또는 서버 사이드 프록시 사용
      let apiBaseUrl;
      if (process.env.NEXT_PUBLIC_API_URL) {
        apiBaseUrl = process.env.NEXT_PUBLIC_API_URL;
      } else if (isDevelopment) {
        apiBaseUrl = 'http://localhost:8000';
      } else {
        // 프로덕션: Mixed Content 문제를 피하기 위해 Next.js rewrites 사용
        // rewrites는 서버 사이드에서 실행되므로 HTTPS → HTTP 문제 없음
        apiBaseUrl = '/api';
      }

      // 디버깅: 실제 요청 URL 로그
      const requestUrl = `${apiBaseUrl}${endpoint}`;
      console.log('🔍 API 요청 디버깅 정보:');
      console.log('  - API Base URL:', apiBaseUrl);
      console.log('  - Endpoint:', endpoint);
      console.log('  - 전체 URL:', requestUrl);
      console.log('  - 환경 변수:', process.env.NEXT_PUBLIC_API_URL || '설정되지 않음');
      console.log('  - 개발 환경:', isDevelopment);

      let response;
      try {
        response = await fetch(requestUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(requestBody),
        });
      } catch (fetchError) {
        // 네트워크 오류 (CORS, Mixed Content, 연결 실패 등)
        console.error('Fetch 오류:', fetchError);
        const errorMsg = fetchError instanceof Error
          ? fetchError.message
          : '네트워크 연결에 실패했습니다.';

        // Mixed Content 오류인지 확인
        if (errorMsg.includes('Mixed Content') || errorMsg.includes('blocked')) {
          throw new Error('HTTPS 사이트에서 HTTP API를 호출할 수 없습니다. Vercel 환경 변수에 NEXT_PUBLIC_API_URL을 설정하거나 Next.js rewrites를 사용하세요.');
        }

        throw new Error(`연결 실패: ${errorMsg}. API 서버가 실행 중인지 확인하세요.`);
      }

      if (!response.ok) {
        // 서버에서 보낸 에러 메시지 파싱
        let errorMessage = "요청에 실패했습니다.";
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch {
          // JSON 파싱 실패 시 기본 메시지 사용
          errorMessage = `요청에 실패했습니다. (${response.status} ${response.statusText})`;
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();

      // 엔드포인트 모드에 따라 응답 처리
      let assistantMessage: Message;
      let sources: any[] = [];
      let answer = "";

      if (endpointMode === "search") {
        // 검색만: results 배열
        sources = data.results || [];
        answer = `검색 결과 ${sources.length}개를 찾았습니다.`;
        assistantMessage = {
          id: (Date.now() + 1).toString(),
          type: "assistant",
          content: answer,
          timestamp: new Date(),
          results: sources,
        };
      } else if (endpointMode === "chat") {
        // 채팅만: answer만
        answer = data.answer || "답변을 생성할 수 없습니다.";
        assistantMessage = {
          id: (Date.now() + 1).toString(),
          type: "assistant",
          content: answer,
          timestamp: new Date(),
        };
      } else {
        // 통합: answer + sources
        answer = data.answer || searchQuery;
        sources = data.sources || [];
        assistantMessage = {
          id: (Date.now() + 1).toString(),
          type: "assistant",
          content: answer,
          timestamp: new Date(),
          results: sources,
        };
      }

      setMessages((prev) => [...prev, assistantMessage]);

      // 비용 추정
      const costEstimate = estimateCost(searchQuery, answer, sources);
      const responseTime = Date.now() - startTime;

      setStats((prev) => ({
        totalSearches: prev.totalSearches + 1,
        avgResults: sources.length || 0,
        responseTime: responseTime,
        totalTokens: prev.totalTokens + costEstimate.tokens,
        estimatedCost: prev.estimatedCost + costEstimate.cost,
      }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "알 수 없는 오류가 발생했습니다.");
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "assistant",
        content: `오류: ${err instanceof Error ? err.message : "알 수 없는 오류가 발생했습니다."}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        width: "100%",
        background: "linear-gradient(135deg, #E8D5FF 0%, #FFD5E5 25%, #D5F0FF 50%, #E5FFF0 75%, #FFF0E5 100%)",
        backgroundSize: "400% 400%",
        animation: "gradient 15s ease infinite",
        position: "relative",
        fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Helvetica Neue', Helvetica, Arial, sans-serif",
        display: "flex",
        flexDirection: "column",
      }}
    >
      {/* 배경 장식 요소 */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: "radial-gradient(circle at 20% 50%, rgba(255, 255, 255, 0.1) 0%, transparent 50%), radial-gradient(circle at 80% 80%, rgba(255, 255, 255, 0.1) 0%, transparent 50%)",
          pointerEvents: "none",
        }}
      />

      {/* 상단 네비게이션 */}
      <nav
        style={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          zIndex: 100,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: "1rem 1.5rem",
          backgroundColor: "rgba(255, 255, 255, 0.15)",
          backdropFilter: "blur(20px)",
          borderBottom: "1px solid rgba(255, 255, 255, 0.2)",
          boxShadow: "0 4px 16px rgba(0, 0, 0, 0.05)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <div
            style={{
              width: "40px",
              height: "40px",
              borderRadius: "12px",
              background: "linear-gradient(135deg, #E8D5FF 0%, #FFD5E5 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#1d1d1f",
              fontSize: "1.25rem",
              fontWeight: 700,
            }}
          >
            R
          </div>
          <div>
            <div style={{ color: "#1d1d1f", fontSize: "1rem", fontWeight: 600 }}>
              RAG 챗봇
            </div>
            <div style={{ color: "rgba(29, 29, 31, 0.7)", fontSize: "0.75rem" }}>
              LangChain × pgvector
            </div>
          </div>
        </div>
        <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", flexWrap: "wrap" }}>
          {/* 엔드포인트 모드 선택 */}
          <div
            style={{
              display: "flex",
              gap: "0.25rem",
              padding: "0.25rem",
              borderRadius: "12px",
              backgroundColor: "rgba(255, 255, 255, 0.2)",
            }}
          >
            {(["search", "chat", "rag"] as EndpointMode[]).map((mode) => (
              <button
                key={mode}
                onClick={() => setEndpointMode(mode)}
                style={{
                  padding: "0.375rem 0.75rem",
                  borderRadius: "8px",
                  border: "none",
                  backgroundColor: endpointMode === mode
                    ? "rgba(255, 255, 255, 0.4)"
                    : "transparent",
                  color: "#1d1d1f",
                  fontSize: "0.75rem",
                  fontWeight: endpointMode === mode ? 600 : 500,
                  cursor: "pointer",
                  transition: "all 0.2s ease",
                }}
                onMouseEnter={(e) => {
                  if (endpointMode !== mode) {
                    e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.2)";
                  }
                }}
                onMouseLeave={(e) => {
                  if (endpointMode !== mode) {
                    e.currentTarget.style.backgroundColor = "transparent";
                  }
                }}
              >
                {mode === "search" ? "검색" : mode === "chat" ? "채팅" : "통합"}
              </button>
            ))}
          </div>

          {/* 통계 및 비용 모니터링 */}
          <div
            style={{
              padding: "0.5rem 1rem",
              borderRadius: "12px",
              backgroundColor: "rgba(255, 255, 255, 0.3)",
              color: "#1d1d1f",
              fontSize: "0.875rem",
              fontWeight: 500,
            }}
          >
            <span style={{ opacity: 0.8 }}>총 대화:</span> {stats.totalSearches}
          </div>

          {stats.totalTokens > 0 && (
            <div
              style={{
                padding: "0.5rem 1rem",
                borderRadius: "12px",
                backgroundColor: "rgba(255, 255, 255, 0.3)",
                color: "#1d1d1f",
                fontSize: "0.875rem",
                fontWeight: 500,
              }}
            >
              <span style={{ opacity: 0.8 }}>토큰:</span> {stats.totalTokens.toLocaleString()}
            </div>
          )}

          {stats.estimatedCost > 0 && (
            <div
              style={{
                padding: "0.5rem 1rem",
                borderRadius: "12px",
                backgroundColor: "rgba(255, 255, 255, 0.3)",
                color: "#1d1d1f",
                fontSize: "0.875rem",
                fontWeight: 500,
              }}
            >
              <span style={{ opacity: 0.8 }}>예상 비용:</span> ${stats.estimatedCost.toFixed(6)}
            </div>
          )}
        </div>
      </nav>

      {/* 메시지 영역 */}
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          padding: "2rem 1.5rem",
          position: "relative",
          zIndex: 1,
          marginTop: "80px", // 네비게이션 높이만큼 여백 추가
          paddingBottom: "120px", // 입력창 높이만큼 하단 여백 추가
        }}
      >
        <div
          style={{
            maxWidth: "900px",
            margin: "0 auto",
            display: "flex",
            flexDirection: "column",
            gap: "1.5rem",
          }}
        >
          {messages.length === 0 && (
            <div
              style={{
                textAlign: "center",
                padding: "3rem 2rem",
                borderRadius: "24px",
                background: "rgba(255, 255, 255, 0.15)",
                backdropFilter: "blur(20px)",
                border: "1px solid rgba(255, 255, 255, 0.2)",
                boxShadow: "0 8px 32px rgba(0, 0, 0, 0.1)",
              }}
            >
              <div
                style={{
                  display: "inline-block",
                  marginBottom: "1rem",
                  padding: "0.5rem 1.25rem",
                  borderRadius: "20px",
                  backgroundColor: "rgba(255, 255, 255, 0.3)",
                  color: "#1d1d1f",
                  fontSize: "0.875rem",
                  fontWeight: 600,
                }}
              >
                ✨ AI 기반 검색
              </div>
              <h1
                style={{
                  color: "#1d1d1f",
                  fontSize: "clamp(2rem, 5vw, 3rem)",
                  fontWeight: 800,
                  letterSpacing: "-0.05em",
                  lineHeight: "1.1",
                  marginBottom: "1rem",
                }}
              >
                지능형 RAG 챗봇
              </h1>
              <p
                style={{
                  color: "rgba(29, 29, 31, 0.8)",
                  fontSize: "1.125rem",
                  fontWeight: 400,
                  lineHeight: "1.6",
                }}
              >
                LangChain과 pgvector를 활용한 고급 의미 기반 검색으로 정확하고 빠른 결과를 제공합니다.
              </p>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              style={{
                display: "flex",
                justifyContent: message.type === "user" ? "flex-end" : "flex-start",
                marginBottom: "0.5rem",
              }}
            >
              <div
                style={{
                  maxWidth: "75%",
                  padding: "1.25rem 1.5rem",
                  borderRadius: message.type === "user" ? "20px 20px 4px 20px" : "20px 20px 20px 4px",
                  backgroundColor:
                    message.type === "user"
                      ? "rgba(255, 255, 255, 0.4)"
                      : "rgba(255, 255, 255, 0.15)",
                  backdropFilter: "blur(20px)",
                  border: "1px solid rgba(255, 255, 255, 0.3)",
                  boxShadow: "0 4px 16px rgba(0, 0, 0, 0.1)",
                }}
              >
                {message.type === "user" ? (
                  <div style={{ color: "#1d1d1f", fontSize: "1rem", fontWeight: 500 }}>
                    {message.content}
                  </div>
                ) : (
                  <div>
                    {/* LLM 답변 표시 */}
                    <div
                      style={{
                        color: "#1d1d1f",
                        fontSize: "1rem",
                        lineHeight: "1.6",
                        marginBottom: message.results && message.results.length > 0 ? "1.5rem" : "0",
                        whiteSpace: "pre-wrap",
                      }}
                    >
                      {message.content}
                    </div>

                    {/* 검색 결과 표시 */}
                    {message.results && message.results.length > 0 && (
                      <>
                        <div
                          style={{
                            marginTop: "1.5rem",
                            paddingTop: "1.5rem",
                            borderTop: "1px solid rgba(255, 255, 255, 0.2)",
                          }}
                        >
                          <div
                            style={{
                              color: "#1d1d1f",
                              fontSize: "0.875rem",
                              fontWeight: 600,
                              marginBottom: "1rem",
                              opacity: 0.8,
                            }}
                          >
                            참고 문서 ({message.results.length}개)
                          </div>
                          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                            {message.results.map((result, index) => (
                              <div
                                key={index}
                                style={{
                                  padding: "1rem",
                                  borderRadius: "12px",
                                  backgroundColor: "rgba(255, 255, 255, 0.2)",
                                  border: "1px solid rgba(255, 255, 255, 0.3)",
                                }}
                              >
                                <div
                                  style={{
                                    display: "flex",
                                    alignItems: "center",
                                    gap: "0.75rem",
                                    marginBottom: "0.75rem",
                                  }}
                                >
                                  <div
                                    style={{
                                      width: "28px",
                                      height: "28px",
                                      borderRadius: "8px",
                                      background: "linear-gradient(135deg, rgba(255, 255, 255, 0.5) 0%, rgba(255, 255, 255, 0.4) 100%)",
                                      color: "#1d1d1f",
                                      display: "flex",
                                      alignItems: "center",
                                      justifyContent: "center",
                                      fontSize: "0.875rem",
                                      fontWeight: 700,
                                    }}
                                  >
                                    {index + 1}
                                  </div>
                                  {result.score !== undefined && (
                                    <div
                                      style={{
                                        fontSize: "0.75rem",
                                        color: "rgba(29, 29, 31, 0.7)",
                                        fontWeight: 500,
                                        padding: "0.25rem 0.625rem",
                                        borderRadius: "8px",
                                        backgroundColor: "rgba(255, 255, 255, 0.3)",
                                      }}
                                    >
                                      유사도: {(result.score * 100).toFixed(1)}%
                                    </div>
                                  )}
                                </div>
                                <p
                                  style={{
                                    color: "#1d1d1f",
                                    fontSize: "0.9375rem",
                                    lineHeight: "1.6",
                                    marginBottom: "0.75rem",
                                  }}
                                >
                                  {result.content}
                                </p>
                                {result.metadata && Object.keys(result.metadata).length > 0 && (
                                  <div
                                    style={{
                                      display: "flex",
                                      flexWrap: "wrap",
                                      gap: "0.5rem",
                                      paddingTop: "0.75rem",
                                      borderTop: "1px solid rgba(255, 255, 255, 0.2)",
                                    }}
                                  >
                                    {Object.entries(result.metadata).map(([key, value]) => (
                                      <span
                                        key={key}
                                        style={{
                                          fontSize: "0.75rem",
                                          padding: "0.375rem 0.625rem",
                                          borderRadius: "8px",
                                          backgroundColor: "rgba(255, 255, 255, 0.25)",
                                          color: "#1d1d1f",
                                          fontWeight: 500,
                                        }}
                                      >
                                        <span style={{ opacity: 0.7 }}>{key}:</span> {String(value)}
                                      </span>
                                    ))}
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      </>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div
              style={{
                display: "flex",
                justifyContent: "flex-start",
              }}
            >
              <div
                style={{
                  padding: "1.25rem 1.5rem",
                  borderRadius: "20px 20px 20px 4px",
                  backgroundColor: "rgba(255, 255, 255, 0.15)",
                  backdropFilter: "blur(20px)",
                  border: "1px solid rgba(255, 255, 255, 0.3)",
                  display: "flex",
                  alignItems: "center",
                  gap: "0.75rem",
                }}
              >
                <div
                  style={{
                    width: "20px",
                    height: "20px",
                    border: "3px solid rgba(29, 29, 31, 0.2)",
                    borderTop: "3px solid #1d1d1f",
                    borderRadius: "50%",
                    animation: "spin 1s linear infinite",
                  }}
                />
                <span style={{ color: "#1d1d1f", fontSize: "0.9375rem" }}>검색 중...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* 하단 입력창 */}
      <div
        style={{
          position: "fixed",
          bottom: 0,
          left: 0,
          right: 0,
          zIndex: 100,
          padding: "1.5rem",
          backgroundColor: "rgba(255, 255, 255, 0.1)",
          backdropFilter: "blur(20px)",
          borderTop: "1px solid rgba(255, 255, 255, 0.2)",
        }}
      >
        <div style={{ maxWidth: "900px", margin: "0 auto" }}>
          <SearchInput onSearch={handleSearch} loading={loading} />
        </div>
      </div>

      <style jsx>{`
        @keyframes gradient {
          0% {
            background-position: 0% 50%;
          }
          50% {
            background-position: 100% 50%;
          }
          100% {
            background-position: 0% 50%;
          }
        }
        @keyframes spin {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }
      `}</style>
    </div>
  );
}
