// Appendix pages shown by index.html (✎ Appendix button): extra material kept apart
// from the chapters. Not read aloud.
//
// Each appendix:
//   title    - name shown in the list
//   part     - optional section it belongs to (e.g. "대한민국의 역사와 발전")
//   source   - optional where it comes from in the book
//   timeline - optional [{ date, event }] in order, shown as a timeline
//   points   - optional plain list of lines

window.APPENDIX = [
  {
    // 대단원 정리, after 단원 종합 평가 of 제2편
    title: "한국 현대사의 주요 흐름",
    part: "대한민국의 역사와 발전",
    source: "대단원 정리",
    timeline: [
      { date: "1945. 8. 15.", event: "광복" },
      { date: "1945. 12.", event: "모스크바 3국 외상 회의" },
      { date: "1946", event: "제1차 미·소 공동 위원회 개최" },
      { date: "1947", event: "제2차 미·소 공동 위원회 개최" },
      { date: "1948. 4.", event: "남북 협상" },
      { date: "1948. 5. 10.", event: "5·10 총선거" },
      { date: "1948. 8. 15.", event: "대한민국 정부 수립" },
      { date: "1950. 6. 25.", event: "6·25 전쟁 발발" },
      { date: "1953. 7.", event: "정전 협정 체결" },
      { date: "1960. 3. 15.", event: "3·15 부정 선거" },
      { date: "1960. 4. 19.", event: "4·19 혁명" },
      { date: "1961. 5. 16.", event: "5·16 군사 정변" },
      { date: "1963", event: "박정희 정부 수립" },
      { date: "1972", event: "유신 체제 성립" },
      { date: "1979", event: "10·26 사태" },
      { date: "1980. 5. 18.", event: "5·18 민주화 운동" },
      { date: "1987", event: "6월 민주 항쟁" }
    ]
  }
];
