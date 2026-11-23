# Fluid Physics Lab

게임프로그래밍입문에 사용될 유체 물리 엔진 깃허브입니다

Python과 Pygame으로 만든 2D 입자 기반 유체 엔진이다. SPH로 물의 밀도, 압력, 점성을 계산하고, 두 장면에서 물이 퍼지는 모습과 강체가 뜨고 가라앉는 모습을 비교할 수 있다. Pygame은 창, 입력, 화면 그리기에 사용한다.

## 실행

`FluidPhysicsEngine` 폴더에서 실행한다. Python 3.12 또는 3.13과 Pygame 2.6.1을 사용한다.

```powershell
python -m pip install -r requirements.txt
python main.py
```

부력 장면부터 열려면 `python main.py --scene buoyancy`를 실행한다.

| 조작 | 동작 |
| --- | --- |
| `1`, `2` | 댐 붕괴, 부력 장면 전환 |
| 왼쪽 마우스 드래그 | 커서 주변 물에 힘 가하기 |
| 오른쪽 마우스 누르기 | 물 입자 추가 |
| `Tab` | 속도 색상과 압력 색상 전환 |
| `F` | 부력 켜기 또는 끄기. 부력 장면에서 작동 |
| `Space`, `N` | 일시정지 또는 재생, 정지 상태에서 한 스텝 진행 |
| `R`, `Esc` | 현재 장면 초기화, 종료 |

## 평가 항목과 확인 방법

| 비중 | 엔진에서 다룬 내용 | 실행 화면에서 확인 |
| --- | --- | --- |
| 중요성과 필요성 20% | 자유 표면을 가진 물에 힘을 가하거나 장애물을 두면 흐름이 달라진다. 입자 기반 모델로 그 변화를 실시간 조작 및 관찰할 수 있다. | 댐 장면에서 물을 휘저어 고정 원형 장애물에 닿는 흐름을 바꾼다. |
| 기본 구현 30% | 2D Poly6 밀도 커널, Spiky 압력 기울기, 입자 속도 차를 줄이는 점성, 중력, 반암시적 오일러 적분, 수조 충돌을 구현했다. | `Tab`으로 압력 표시를 켜고 충돌 직후 높은 압력을 확인한다. `N`으로 10ms씩 진행할 수 있다. |
| 심화 구현 50% | 공간 해시로 이웃 후보쌍을 줄인다. 원형 강체의 접촉 충격량과 부력·항력을 계산하고, 동적 강체가 받은 힘의 반작용을 유체에 적용한다. | 부력 장면에서 두 강체의 잠긴 비율과 부력을 비교한다. `F`로 설정을 바꾼 뒤 `R`로 같은 초기 상태를 재생한다. `Grid / all-pairs checks`는 격자가 거리 검사한 후보쌍 수를 전체 입자쌍 수로 나눈 값이다. |

## 파일 구조

```text
main.py                       실행 진입점
scenes.py                     장면과 초기 입자, 강체 배치
engine/
  settings.py                 물리 파라미터와 입자 질량 보정
  particles.py                입자 상태
  rigid.py                    원형 강체 상태와 질량
  spatial_grid.py             이웃 후보쌍과 범위 탐색
  sph.py                      밀도, 압력, 점성 및 진단 수치
  contacts.py                 벽과 원형 강체의 접촉 처리
  coupling.py                 수면 추정, 잠긴 면적, 부력과 항력
  world.py                    물리 갱신 순서와 외부 힘
lab/
  app.py                      입력, 고정 시간 스텝, 실행 루프
  layout.py                   UI 배치와 좌표 변환
  renderer.py                 조작 버튼과 진단 패널
  tank.py                     수조, 입자, 강체 그리기
```

`World.step()`은 격자 재구축 → 밀도와 힘 계산 → 강체 결합 → 속도와 위치 적분 → 충돌 처리 순으로 진행한다. `sph.py`는 입자쌍을 한 번만 방문하고 두 입자에 반대 방향의 힘을 적용한다. `coupling.py`는 강체 양쪽에 모인 입자로 국소 수면 높이를 추정한 뒤, 수면 아래에 있는 원의 면적에 비례해 부력을 계산한다. 이 수면 모델은 물이 강체 옆에 모인 상황을 근사하므로 물보라나 급경사 수면에서는 잠긴 비율이 흔들릴 수 있다.

SPH 참고 문헌은 Müller, Charypar, Gross의 2003년 논문이다. 논문의 입자 기반 접근을 참고해 2D 커널과 수조·강체 상호작용을 구성했다. [Particle-Based Fluid Simulation for Interactive Applications](https://cgl.ethz.ch/Downloads/Publications/Papers/2003/Mue03b/Mue03b.pdf)

프로젝트 저장소 링크는 사용자에게 제공받았다. [FluidPhysicsEngine](https://github.com/seojunyun8/FluidPhysicsEngine)

첨부 과제 공지에는 코드 작성 및 디버깅에 생성형 AI를 사용하지 않는다고 명시되어 있다. 이 프로젝트는 Codex가 작성한 구현이다.
