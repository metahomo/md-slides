---
marp: true
paginate: true
---

<!-- _class: lead -->
# MD 슬라이드 문법 안내

VS Code · nvim 미리 보기와 웹 슬라이드에서 같은 MD 파일이 그대로 보이게

<!-- 이 덱 자체가 예시다. 원본: decks/md-syntax-guide.md -->

---

# 제목은 세 단계

## `##` 장 제목 — 한 장에 하나

### `###` 소제목

- `#` 표지·절 구분(lead) 제목, `##` 보통 장 제목, `###` 장 안의 묶음
- 제목은 결론 한 문장으로 쓴다

---

# 목록 — `-` `+` `*` 모두 된다

+ 더하기 표시로 쓴 목록
+ 들여쓰기 두 칸이면 하위 목록
  + 하위 항목
- 섞어 써도 같은 목록 모양

1. 번호 목록
2. 숫자는 자동으로 이어진다

---

<!-- _class: hangul -->
# 가, 나, 다 순서 목록

<!-- _class: hangul 을 붙인 장은 번호 목록이 가, 나, 다로 나온다 -->

1. 문제 정의
2. 데이터 준비
3. 학습과 검증
4. 배포와 롤백

`<!-- _class: hangul -->` 한 줄을 장 맨 위에

---

# 코드 — 언어 이름과 강조할 줄

```javascript {1,2}
import fs from "node:fs";
const text = fs.readFileSync("deck.md", "utf8");
console.log(text.length);
```

```python
import os
print(os.getcwd())
```

` ```javascript {1,2} ` → 1·2번 줄을 강조 (VS Code 문법 그대로)

---

# 여러 언어 — Go · bun · node

```go
package main

import "fmt"

func main() { fmt.Println("hello") }
```

```bash
bun run build      # bun
node server.js     # node
```

---

# 알림 상자 — `> [!NOTE]`

> [!NOTE]
> VS Code·nvim 미리 보기와 GitHub 에서 그대로 보이는 문법

> [!TIP]
> 한 장에 결론 한 줄 + 표 하나 또는 글머리 3~5줄

> [!WARNING]
> 공유 키·비밀번호는 덱에 넣지 않는다 (덱은 공개된다)

`NOTE` · `TIP` · `IMPORTANT` · `WARNING` · `CAUTION`

---

# 표와 2단

<div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5em">
<div>

| 문법 | 결과 |
|---|---|
| `**굵게**` | **굵게** |
| `` `코드` `` | `코드` |

</div>
<div>

- 2단은 HTML `div` 그리드
- `div` 안 MD 앞뒤에는 빈 줄

</div>
</div>

---

# 단계별 등장과 발표자 노트

- 처음부터 보이는 줄

<p class="fragment">→ 키를 한 번 더 누르면 나오는 줄</p>

<!-- HTML 주석은 발표자 노트가 된다. 발표 중 S 키로 본다. -->

`<p class="fragment">` · 주석 `<!-- … -->` = 발표자 노트

---

<!-- _class: lead -->
<!-- _backgroundColor: #0f172a -->
<!-- _class: lead invert -->
# 장 지시어 (Marp)

`_class: lead` 가운데 · `_class: invert` 어두운 글자색 · `_backgroundColor` 배경

---

# 지시어 한눈에

| 주석 한 줄 | 효과 |
|---|---|
| `<!-- _class: lead -->` | 가운데 정렬 표지·절 구분 |
| `<!-- _class: hangul -->` | 번호 목록 가, 나, 다 |
| `<!-- _class: small -->` | 글이 많은 장 글자 줄이기 |
| `<!-- _backgroundColor: #0f172a -->` | 장 배경색 |
| `<!-- _backgroundImage: url(그림주소) -->` | 장 배경 그림 |

여러 클래스는 띄어 쓴다: `<!-- _class: lead invert -->`
