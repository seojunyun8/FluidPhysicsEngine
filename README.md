# Fluid Physics Lab

수조 안에서 물 입자가 떨어지고 퍼지는 2D 시뮬레이션이다. 수조 안을 클릭하면 주황색 공이 떨어진다. 공과 물 입자가 부딪히면 양쪽 속도가 달라진다.

## 실행

Python 3.12 또는 3.13과 Pygame 2.6.1을 사용한다.

### VS Code

1. ZIP으로 받았다면 먼저 압축을 푼다. VS Code의 **파일 → 파일에서 작업 영역 열기**에서 `FluidPhysicsEngine.code-workspace`를 선택한다.
2. 권장 확장인 Microsoft의 **Python**과 **Python Debugger**를 설치한다. `Ctrl+Shift+P` → `Python: Select Interpreter`에서 사용할 Python 3.12 또는 3.13을 선택한다.
3. 선택한 환경에 Pygame이 없다면 VS Code에서 새 터미널을 열고 `python -m pip install -r requirements.txt`를 실행한다.
4. `F5`로 **Fluid Physics Lab**을 실행한다.

### 터미널

`FluidPhysicsEngine` 폴더에서 실행한다.

```powershell
python -m pip install -r requirements.txt
python main.py
```

| 조작 | 동작 |
| --- | --- |
| `1` | 시뮬레이션 시작 및 다시 시작 |
| 왼쪽 마우스 클릭 | 클릭한 위치에 공 떨어뜨리기. 첫 클릭으로도 시작 가능 |
| 왼쪽 마우스 드래그 | 커서 주변 물에 힘 가하기 |
| 오른쪽 마우스 누르기 | 물 입자 추가 |
| `Esc` | 종료 |

## 파일 구조

```text
main.py                       실행 진입점
scenes.py                     수조와 초기 입자 배치
engine/
  settings.py                 물리 파라미터와 입자 질량 보정
  particles.py                입자 상태
  spatial_grid.py             이웃 후보쌍과 범위 탐색
  sph.py                      밀도, 압력, 점성 계산
  rigid.py                    공의 위치, 속도, 반지름, 질량
  contacts.py                 수조 벽, 공, 물 입자 사이의 충돌
  world.py                    물리 갱신 순서와 외부 힘
lab/
  app.py                      입력, 고정 시간 스텝, 실행 루프
  layout.py                   수조 배치와 좌표 변환
  tank.py                     수조, 물 입자, 공 그리기
```

`World.step()`은 1/120초마다 실행된다. SPH로 물의 밀도와 압력, 점성을 계산하고 위치를 갱신한다. 공의 질량은 1.5, 반지름은 0.42이며 수조에 최대 12개까지 둘 수 있다. 공과 물 입자 또는 두 공이 겹치며 서로 다가올 때 충격량을 적용한다. 질량이 작은 쪽의 속도가 더 크게 변한다.

SPH 참고 문헌은 Müller, Charypar, Gross의 2003년 논문이다. [Particle-Based Fluid Simulation for Interactive Applications](https://cgl.ethz.ch/Downloads/Publications/Papers/2003/Mue03b/Mue03b.pdf)

이 프로젝트의 엔진 구현과 원형 물체 추가에는 Codex를 사용했다. 과제 공지는 코드 작성·디버깅에 생성형 AI를 사용하지 않는다고 명시한다.
