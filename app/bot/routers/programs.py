from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import Session

from app.infra.db.session import get_session
from app.domain.services.catalog_service import CatalogService, MUSCLE_GROUPS

router = Router(name=__name__)


@router.callback_query(F.data.startswith("prog:level:"))
async def pick_level(call: CallbackQuery) -> None:
	level = call.data.split(":", 2)[2]
	kb = InlineKeyboardBuilder()
	kb.button(text="Сплит", callback_data=f"prog:type:split:{level}")
	kb.button(text="Дом", callback_data=f"prog:type:home:{level}")
	kb.button(text="Улица", callback_data=f"prog:type:street:{level}")
	kb.button(text="Зал", callback_data=f"prog:type:gym:{level}")
	kb.adjust(2)
	await call.message.edit_text("Выберите тип программы")
	await call.message.edit_reply_markup(reply_markup=kb.as_markup())
	await call.answer()


@router.callback_query(F.data.startswith("prog:type:"))
async def pick_type(call: CallbackQuery) -> None:
	_, _, type_, level = call.data.split(":", 3)
	kb = InlineKeyboardBuilder()
	for mg in MUSCLE_GROUPS:
		text = {
			"back": "Спина",
			"biceps": "Бицепс",
			"triceps": "Трицепс",
			"shoulders": "Плечи",
			"legs": "Ноги",
			"forearms": "Предплечья",
		}[mg]
		kb.button(text=text, callback_data=f"prog:mg:{mg}:{type_}:{level}")
	kb.adjust(2)
	await call.message.edit_text("Выберите группу мышц")
	await call.message.edit_reply_markup(reply_markup=kb.as_markup())
	await call.answer()


@router.callback_query(F.data.startswith("prog:mg:"))
async def show_programs(call: CallbackQuery) -> None:
	_, _, mg, type_, level = call.data.split(":", 4)
	with get_session() as session:  # type: Session
		catalog = CatalogService(session)
		catalog.seed_all()
		views = catalog.list_programs(level=level, type_=type_, muscle_group=mg)
	kb = InlineKeyboardBuilder()
	for pv in views[:10]:
		kb.button(text=pv.program.name, callback_data=f"prog:show:{pv.program.id}:{level}:{type_}")
	kb.adjust(1)
	await call.message.edit_text(f"Программы для {mg} — {level}/{type_}")
	await call.message.edit_reply_markup(reply_markup=kb.as_markup())
	await call.answer()


@router.callback_query(F.data.startswith("prog:show:"))
async def show_program_detail(call: CallbackQuery) -> None:
	_, _, pid, level, type_ = call.data.split(":", 4)
	program_id = int(pid)
	with get_session() as session:  # type: Session
		from sqlalchemy import select
		from app.domain.models.program import ProgramExercise, WorkoutProgram
		from app.domain.models.exercise import Exercise
		pe = session.scalars(select(ProgramExercise).where(ProgramExercise.program_id == program_id).order_by(ProgramExercise.order_index)).all()
		ex_ids = [x.exercise_id for x in pe]
		exs = session.scalars(select(Exercise).where(Exercise.id.in_(ex_ids))).all()
		prog = session.get(WorkoutProgram, program_id)
	kb = InlineKeyboardBuilder()
	# Выбор сложности
	for diff in ["Лёгкая", "Средняя", "Сложная"]:
		kb.button(text=diff, callback_data=f"prog:diff:{program_id}:{level}:{type_}:{diff}")
	kb.adjust(3)
	desc = f"{prog.name}\nУпражнения:\n" + "\n".join(f"• {ex.name}" for ex in exs)
	await call.message.edit_text(desc + "\nВыберите сложность для подбора весов:")
	await call.message.edit_reply_markup(reply_markup=kb.as_markup())
	await call.answer()


@router.callback_query(F.data.startswith("prog:diff:"))
async def choose_goal_and_weights(call: CallbackQuery) -> None:
	_, _, pid, level, type_, diff = call.data.split(":", 5)
	program_id = int(pid)
	kb = InlineKeyboardBuilder()
	for goal in ["Похудеть", "Набор массы", "Сушка", "Поддерживать форму"]:
		kb.button(text=goal, callback_data=f"prog:goal:{program_id}:{level}:{type_}:{diff}:{goal}")
	kb.adjust(2)
	await call.message.edit_text("Выберите цель тренировки:")
	await call.message.edit_reply_markup(reply_markup=kb.as_markup())
	await call.answer()


def _weight_hint(diff: str, goal: str) -> str:
	# Простая эвристика: % от 1ПМ (one-rep max) — пользователь без теста: даём ориентир в РПЕ
	base = {
		"Лёгкая": "РПЕ 6–7 (~60–70% от 1ПМ)",
		"Средняя": "РПЕ 7–8 (~70–80% от 1ПМ)",
		"Сложная": "РПЕ 8–9 (~80–90% от 1ПМ)",
	}[diff]
	focus = {
		"Похудеть": "Больше повторов, короче отдых",
		"Набор массы": "Средний диапазон повторов, прогрессия веса",
		"Сушка": "Контроль темпа и пауз, умеренный вес",
		"Поддерживать форму": "Умеренная нагрузка, стабильный объём",
	}[goal]
	return f"Рекомендация: {base}. {focus}. Начните консервативно и прогрессируйте."


@router.callback_query(F.data.startswith("prog:goal:"))
async def show_weights(call: CallbackQuery) -> None:
	_, _, pid, level, type_, diff, goal = call.data.split(":", 6)
	# Здесь можно сохранить выбор пользователя в БД (опущено для краткости)
	hint = _weight_hint(diff, goal)
	await call.message.edit_text(f"Сложность: {diff}\nЦель: {goal}\n{hint}")
	await call.message.edit_reply_markup(reply_markup=None)
	await call.answer()