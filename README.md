# Fluid Physics Lab

게임프로그래밍입문에 사용될 유체 물리 엔진 깃허브입니다

Python과 Pygame으로 만든 2D 입자 기반 유체 엔진이다. `1`을 누르면 작은 물 입자들이 수조 안에서 떨어지고 벽에 부딪히며 퍼진다. SPH로 밀도, 압력, 점성을 계산한다.

## 실행

Python 3.12 또는 3.13과 Pygame 2.6.1을 사용한다.

### VS Code

1. ZIP으로 받았다면 먼저 압축을 푼다. VS Code의 **파일 → 파일에서 작업 영역 열기**에서 `FluidPhysicsEngine.code-workspace`를 선택한다.
2. 권장 확장인 Microsoft의 **Python**과 **Python Debugger**를 설치한다. `Ctrl+Shift+P` → `Python: Select Interpreter`에서 사용할 Python 3.12 또는 3.13을 선택한다.
3. 선택한 환경에 Pygame이 없다면 VS Code에서 새 터미널을 열고 `python -m pip install -r requirements.txt`를 실행한다.
4. `F5`로 **Fluid Physics Lab**을 실행한 뒤, 시뮬레이션 창에서 `1`을 누른다.

### 터미널

`FluidPhysicsEngine` 폴더에서 실행한다.

```powershell
python -m pip install -r requirements.txt
python main.py
```

| 조작 | 동작 |
| --- | --- |
| `1` | 시뮬레이션 시작 및 다시 시작 |
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
  contacts.py                 입자와 수조 벽의 충돌 처리
  world.py                    물리 갱신 순서와 외부 힘
lab/
  app.py                      입력, 고정 시간 스텝, 실행 루프
  layout.py                   수조 배치와 좌표 변환
  tank.py                     수조와 물 입자 그리기
```

`World.step()`은 120Hz 고정 시간 스텝으로 격자 재구축, 밀도와 힘 계산, 속도와 위치 적분, 벽 충돌 처리를 차례로 진행한다. 공간 해시로 가까운 셀의 입자만 비교하고, 각 이웃 쌍의 두 입자에 반대 방향의 힘을 가한다. 화면에서는 촘촘한 입자의 밑색을 겹쳐 물줄기가 이어져 보이게 그린다.

SPH 참고 문헌은 Müller, Charypar, Gross의 2003년 논문이다. [Particle-Based Fluid Simulation for Interactive Applications](https://cgl.ethz.ch/Downloads/Publications/Papers/2003/Mue03b/Mue03b.pdf)

프로젝트 저장소 링크는 사용자에게 제공받았다. [FluidPhysicsEngine](https://github.com/seojunyun8/FluidPhysicsEngine)

첨부 과제 공지에는 코드 작성 및 디버깅에 생성형 AI를 사용하지 않는다고 명시되어 있다. 이 프로젝트는 Codex가 작성한 구현이다.
