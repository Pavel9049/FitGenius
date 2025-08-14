from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import Session

from app.infra.db.session import get_session
from app.domain.services.catalog_service import CatalogService, MUSCLE_GROUPS
from app.domain.services.workouts_service import WorkoutsService
from app.bot.utils.animations import evaporate_and_edit
from app.domain.services.banner_service import get_header

router = Router(name=__name__)

GOALS = ["Похудеть", "Набор массы", "Сушка", "Поддерживать форму"]


@router.callback_query(F.data.startswith("prog:level:"))
async def pick_level(call: CallbackQuery) -> None:
	level = call.data.split(":", 2)[2]
	if level in ("novice", "advanced", "pro"):
		kb = InlineKeyboardBuilder()
		for g in GOALS:
			kb.button(text=g, callback_data=f"prog:setgoal:{level}:{g}")
		kb.adjust(2)
		header = get_header()
		await evaporate_and_edit(call.message, f"{header}\nВыберите вашу цель тренировки:", reply_markup=kb.as_markup())
		await call.answer()
		return
	kb = InlineKeyboardBuilder()
	kb.button(text="Сплит", callback_data=f"prog:type:split:{level}")
	kb.button(text="Дом", callback_data=f"prog:type:home:{level}")
	kb.button(text="Улица", callback_data=f"prog:type:street:{level}")
	kb.button(text="Зал", callback_data=f"prog:type:gym:{level}")
	kb.adjust(2)
	header = get_header()
	await evaporate_and_edit(call.message, f"{header}\nВыберите тип программы", reply_markup=kb.as_markup())
	await call.answer()


@router.callback_query(F.data.startswith("prog:setgoal:"))
async def set_goal(call: CallbackQuery, lang: str) -> None:
	_, _, level, goal = call.data.split(":", 3)
	with get_session() as session:  # type: Session
		service = WorkoutsService(session)
		user = service.ensure_user(tg_id=call.from_user.id, language=lang)
		user.training_goal = goal
		session.commit()
	kb = InlineKeyboardBuilder()
	kb.button(text="Сплит", callback_data=f"prog:type:split:{level}")
	kb.button(text="Дом", callback_data=f"prog:type:home:{level}")
	kb.button(text="Улица", callback_data=f"prog:type:street:{level}")
	kb.button(text="Зал", callback_data=f"prog:type:gym:{level}")
	kb.adjust(2)
	header = get_header()
	await evaporate_and_edit(call.message, f"{header}\nЦель сохранена: {goal}. Теперь выберите тип программы:", reply_markup=kb.as_markup())
	await call.answer()


@router.callback_query(F.data.startswith("prog:type:"))
async def pick_type(call: CallbackQuery) -> None:
	_, _, type_, level = call.data.split(":", 3)
	kb = InlineKeyboardBuilder()
	for mg in MUSCLE_GROUPS:
		if mg == "core":
			continue
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
	header = get_header()
	await evaporate_and_edit(call.message, f"{header}\nВыберите группу мышц", reply_markup=kb.as_markup())
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
	header = get_header()
	await evaporate_and_edit(call.message, f"{header}\nПрограммы для {mg} — {level}/{type_}", reply_markup=kb.as_markup())
	await call.answer()


_CORE_LIMIT = {"beginner": 3, "novice": 4, "advanced": 5, "pro": 6}


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
		ex_map = {e.id: e for e in session.scalars(select(Exercise).where(Exercise.id.in_(ex_ids))).all()}
		lines = []
		for row in pe:
			ex = ex_map.get(row.exercise_id)
			if not ex:
				continue
			meta = []
			if row.sets_desc:
				meta.append(row.sets_desc)
			if row.rest_desc:
				meta.append(row.rest_desc)
			meta_str = f" ({', '.join(meta)})" if meta else ""
			if row.tip_text:
				lines.append(f"• {ex.name}{meta_str}\n  💡 {row.tip_text}")
			else:
				lines.append(f"• {ex.name}{meta_str}")
		if type_ == "gym" or type_ == "split":
			core_pool = session.scalars(select(Exercise).where(Exercise.muscle_group == "core", Exercise.equipment == "gym")).all()
		else:
			core_pool = session.scalars(select(Exercise).where(Exercise.muscle_group == "core", Exercise.equipment == "bodyweight")).all()
		limit = _CORE_LIMIT.get(level, 3)
		for ex in core_pool[:limit]:
			lines.append(f"• {ex.name} (пресс)")
		prog = session.get(WorkoutProgram, program_id)
	kb = InlineKeyboardBuilder()
	for diff in ["🔹 Лёгкая", "🔸 Средняя", "🔺 Сложная"]:
		kb.button(text=diff + "  ⟶", callback_data=f"prog:diff:{program_id}:{level}:{type_}:{diff.split()[1]}")
	kb.adjust(1)
	header = get_header()
	desc = f"{header}\n{prog.name}\nУпражнения:\n" + "\n".join(lines)
	await evaporate_and_edit(call.message, desc + "\nВыберите сложность для подбора весов:", reply_markup=kb.as_markup())
	await call.answer()


@router.callback_query(F.data.startswith("prog:diff:"))
async def choose_goal_and_weights(call: CallbackQuery) -> None:
	_, _, pid, level, type_, diff = call.data.split(":", 5)
	program_id = int(pid)
	with get_session() as session:
		from sqlalchemy import select
		from app.domain.models.program import ProgramExercise
		from app.domain.models.user import User
		service = WorkoutsService(session)
		user = session.scalar(select(User).where(User.tg_id == call.from_user.id))
		pe = session.scalars(select(ProgramExercise).where(ProgramExercise.program_id == program_id).order_by(ProgramExercise.order_index)).all()
		recs = []
		for row in pe:
			w = service.suggest_weight(user, row.exercise_id, diff, user.training_goal or "Поддерживать форму")
			recs.append((row.exercise_id, w))
	kb = InlineKeyboardBuilder()
	for goal in GOALS:
		kb.button(text=f"🎯 {goal}   ⟶", callback_data=f"prog:goal:{program_id}:{level}:{type_}:{diff}:{goal}")
	kb.adjust(1)
	header = get_header()
	lines = []
	for (ex_id, w) in recs[:6]:
		if w is None:
			lines.append("• Вес: по РПЕ 6–8 (нет данных)")
		else:
			lines.append(f"• Реком. вес: {w} кг")
	await evaporate_and_edit(call.message, f"{header}\nСложность: {diff}\nПредварительный подбор весов:\n" + "\n".join(lines) + "\nВыберите цель для уточнения:", reply_markup=kb.as_markup())
	await call.answer()


def _weight_hint(diff: str, goal: str) -> str:
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
	header = get_header()
	hint = _weight_hint(diff, goal)
	await evaporate_and_edit(call.message, f"{header}\nСложность: {diff}\nЦель: {goal}\n{hint}")
	await call.answer()