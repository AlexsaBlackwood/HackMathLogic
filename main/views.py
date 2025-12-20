from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from main.forms import SubThemeForm, UserRegistrationForm, UserLoginForm
from main.models import Theme, SubTheme, Article, Test, TestQuestion, TestAnswerVariant, UserProfile, Result, ResultItem
from django.core.exceptions import PermissionDenied


def index_page(request):
    return render(request, "index.html")


# ------------------------
# Миксины для проверки прав
# ------------------------
class RoleRequiredMixin:
    """Базовый миксин для проверки роли пользователя"""
    required_roles = []
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Необходима авторизация.')
            return redirect('login')
        
        if not hasattr(request.user, 'profile'):
            messages.error(request, 'Профиль пользователя не найден.')
            return redirect('login')
        
        if self.required_roles and request.user.profile.role not in self.required_roles:
            messages.error(request, 'У вас нет прав для выполнения этого действия.')
            return redirect('index')
        
        return super().dispatch(request, *args, **kwargs)


class TeacherRequiredMixin(RoleRequiredMixin):
    """Доступ только для преподавателей и администраторов"""
    required_roles = ['TEACHER', 'ADMIN']


class AdminRequiredMixin(RoleRequiredMixin):
    """Доступ только для администраторов"""
    required_roles = ['ADMIN']


# ------------------------
# Авторизация
# ------------------------
class RegisterView(View):
    template_name = 'auth/register.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('index')
        form = UserRegistrationForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Аккаунт {username} успешно создан!')
            login(request, user)
            return redirect('index')
        return render(request, self.template_name, {'form': form})


class LoginView(View):
    template_name = 'auth/login.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('index')
        form = UserLoginForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}!')
                return redirect('index')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль.')
        return render(request, self.template_name, {'form': form})


class LogoutView(DjangoLogoutView):
    next_page = 'index'


class ThemeBaseMixin:
    model = Theme
    pk_url_kwarg = 'id'
    fields = ["title"]


class ThemeListView(RoleRequiredMixin, ThemeBaseMixin, ListView):
    template_name = 'themes/list.html'
    required_roles = []  # Доступно всем авторизованным


class ThemeDetailView(RoleRequiredMixin, ThemeBaseMixin, DetailView):
    template_name = 'themes/view.html'
    required_roles = []  # Доступно всем авторизованным


class ThemeAddView(TeacherRequiredMixin, ThemeBaseMixin, CreateView):
    template_name = 'themes/add.html'


class ThemeEditView(TeacherRequiredMixin, ThemeBaseMixin, UpdateView):
    template_name = 'themes/edit.html'


class ThemeDeleteView(TeacherRequiredMixin, ThemeBaseMixin, DeleteView):
    success_url = reverse_lazy("themes_list")


class SubThemeBaseMixin:
    model = SubTheme
    pk_url_kwarg = 'st_id'
    form_class = SubThemeForm

    def get_queryset(self):
        return super().get_queryset().select_related('theme')

    def get_theme(self):
        return get_object_or_404(Theme, id=self.kwargs['t_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['theme'] = self.get_theme()
        if not isinstance(self, CreateView):
            context['subtheme'] = self.get_object()
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.pop('instance', None)
        return kwargs

    def save_subtheme_and_article(self, form, subtheme=None):
        if subtheme is None:
            subtheme = SubTheme.objects.create(title=form.cleaned_data['title'], theme=self.get_theme())
            Article.objects.create(text=form.cleaned_data['text'], subtheme=subtheme)
        else:
            article = subtheme.articles.first() or Article(subtheme=subtheme)
            subtheme.title, article.text = form.cleaned_data['title'], form.cleaned_data['text']
            subtheme.save()
            article.save()
        return subtheme

    def get_success_redirect(self, subtheme):
        return redirect(reverse("subtheme_view", kwargs={"t_id": subtheme.theme.id, "st_id": subtheme.id}))


class SubThemeDetailView(RoleRequiredMixin, SubThemeBaseMixin, DetailView):
    template_name = 'subthemes/view.html'
    required_roles = []  # Доступно всем авторизованным


class SubThemeUpdateView(TeacherRequiredMixin, SubThemeBaseMixin, UpdateView):
    template_name = 'subthemes/edit.html'

    def get_initial(self):
        initial = super().get_initial()
        subtheme = self.get_object()
        article = subtheme.articles.first()
        if article:
            initial.update(title=subtheme.title, text=article.text)
        return initial

    def form_valid(self, form):
        return self.get_success_redirect(self.save_subtheme_and_article(form, self.get_object()))


class SubThemeCreateView(TeacherRequiredMixin, SubThemeBaseMixin, CreateView):
    template_name = 'subthemes/add.html'

    def form_valid(self, form):
        return self.get_success_redirect(self.save_subtheme_and_article(form))


class SubThemeDeleteView(TeacherRequiredMixin, SubThemeBaseMixin, DeleteView):
    def get(self, request, *args, **kwargs):
        return redirect(reverse('subtheme_edit', kwargs={"t_id": self.kwargs['t_id'], "st_id": self.kwargs['st_id']}))

    def post(self, request, *args, **kwargs):
        subtheme = self.get_object()
        subtheme.articles.all().delete()
        subtheme.delete()
        return redirect(reverse('theme_view', kwargs={"id": subtheme.theme.id}))


class TestBaseMixin:
    model = Test
    pk_url_kwarg = 'test_id'
    fields = ["question"]

    def get_queryset(self):
        return super().get_queryset().select_related('subtheme', 'subtheme__theme')

    def get_subtheme(self):
        return get_object_or_404(SubTheme, id=self.kwargs['st_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subtheme'] = self.get_subtheme()
        context['theme'] = context['subtheme'].theme
        if not isinstance(self, (CreateView, ListView)) and hasattr(self, 'get_object'):
            context['test'] = self.get_object()
        return context

    def get_success_redirect(self, test):
        return redirect(reverse("test_view", kwargs={"t_id": test.subtheme.theme.id, "st_id": test.subtheme.id, "test_id": test.id}))


class TestListView(RoleRequiredMixin, TestBaseMixin, ListView):
    template_name = 'tests/list.html'
    required_roles = []  # Доступно всем авторизованным

    def get_queryset(self):
        return Test.objects.filter(subtheme_id=self.kwargs['st_id']).select_related('subtheme', 'subtheme__theme')


class TestDetailView(RoleRequiredMixin, TestBaseMixin, DetailView):
    template_name = 'tests/view.html'
    required_roles = []  # Доступно всем авторизованным

    def get_queryset(self):
        return super().get_queryset().prefetch_related('questions__answers')


class TestCreateView(TeacherRequiredMixin, TestBaseMixin, CreateView):
    template_name = 'tests/add.html'

    def form_valid(self, form):
        test = form.save(commit=False)
        test.subtheme = self.get_subtheme()
        test.save()
        return self.get_success_redirect(test)


class TestUpdateView(TeacherRequiredMixin, TestBaseMixin, UpdateView):
    template_name = 'tests/edit.html'

    def form_valid(self, form):
        return self.get_success_redirect(form.save())


class TestDeleteView(TeacherRequiredMixin, TestBaseMixin, DeleteView):
    def get(self, request, *args, **kwargs):
        return redirect(reverse('test_edit', kwargs={"t_id": self.kwargs['t_id'], "st_id": self.kwargs['st_id'], "test_id": self.kwargs['test_id']}))

    def post(self, request, *args, **kwargs):
        test = self.get_object()
        st_id = test.subtheme.id
        t_id = test.subtheme.theme.id
        test.delete()
        return redirect(reverse('subtheme_view', kwargs={"t_id": t_id, "st_id": st_id}))


class TestQuestionBaseMixin:
    model = TestQuestion
    pk_url_kwarg = 'q_id'
    fields = ["text"]

    def get_queryset(self):
        return super().get_queryset().select_related('test', 'test__subtheme', 'test__subtheme__theme')

    def get_test(self):
        return get_object_or_404(Test, id=self.kwargs['test_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['test'] = self.get_test()
        context['subtheme'] = context['test'].subtheme
        context['theme'] = context['subtheme'].theme
        if not isinstance(self, CreateView):
            context['question'] = self.get_object()
        return context

    def get_success_redirect(self, question):
        return redirect(reverse("testquestion_view", kwargs={"t_id": question.test.subtheme.theme.id, "st_id": question.test.subtheme.id, "test_id": question.test.id, "q_id": question.id}))


class TestQuestionDetailView(RoleRequiredMixin, TestQuestionBaseMixin, DetailView):
    template_name = 'testquestions/view.html'
    required_roles = []  # Доступно всем авторизованным


class TestQuestionCreateView(TeacherRequiredMixin, TestQuestionBaseMixin, CreateView):
    template_name = 'testquestions/add.html'

    def form_valid(self, form):
        question = form.save(commit=False)
        question.test = self.get_test()
        question.save()
        return self.get_success_redirect(question)


class TestQuestionUpdateView(TeacherRequiredMixin, TestQuestionBaseMixin, UpdateView):
    template_name = 'testquestions/edit.html'

    def form_valid(self, form):
        return self.get_success_redirect(form.save())


class TestQuestionDeleteView(TeacherRequiredMixin, TestQuestionBaseMixin, DeleteView):
    def get(self, request, *args, **kwargs):
        return redirect(reverse('testquestion_edit', kwargs={"t_id": self.kwargs['t_id'], "st_id": self.kwargs['st_id'], "test_id": self.kwargs['test_id'], "q_id": self.kwargs['q_id']}))

    def post(self, request, *args, **kwargs):
        question = self.get_object()
        test_id = question.test.id
        st_id = question.test.subtheme.id
        t_id = question.test.subtheme.theme.id
        question.delete()
        return redirect(reverse('test_view', kwargs={"t_id": t_id, "st_id": st_id, "test_id": test_id}))


class TestAnswerVariantBaseMixin:
    model = TestAnswerVariant
    pk_url_kwarg = 'a_id'
    fields = ["text", "is_right"]

    def get_queryset(self):
        return super().get_queryset().select_related('question', 'question__test', 'question__test__subtheme', 'question__test__subtheme__theme')

    def get_question(self):
        return get_object_or_404(TestQuestion, id=self.kwargs['q_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['question'] = self.get_question()
        context['test'] = context['question'].test
        context['subtheme'] = context['test'].subtheme
        context['theme'] = context['subtheme'].theme
        if not isinstance(self, CreateView):
            context['answer'] = self.get_object()
        return context

    def get_success_redirect(self, answer):
        return redirect(reverse("testanswervariant_view", kwargs={"t_id": answer.question.test.subtheme.theme.id, "st_id": answer.question.test.subtheme.id, "test_id": answer.question.test.id, "q_id": answer.question.id, "a_id": answer.id}))


class TestAnswerVariantDetailView(RoleRequiredMixin, TestAnswerVariantBaseMixin, DetailView):
    template_name = 'testanswervariants/view.html'
    required_roles = []  # Доступно всем авторизованным


class TestAnswerVariantCreateView(TeacherRequiredMixin, TestAnswerVariantBaseMixin, CreateView):
    template_name = 'testanswervariants/add.html'

    def form_valid(self, form):
        answer = form.save(commit=False)
        answer.question = self.get_question()
        answer.save()
        return self.get_success_redirect(answer)


class TestAnswerVariantUpdateView(TeacherRequiredMixin, TestAnswerVariantBaseMixin, UpdateView):
    template_name = 'testanswervariants/edit.html'

    def form_valid(self, form):
        return self.get_success_redirect(form.save())


class TestAnswerVariantDeleteView(TeacherRequiredMixin, TestAnswerVariantBaseMixin, DeleteView):
    def get(self, request, *args, **kwargs):
        return redirect(reverse('testanswervariant_edit', kwargs={"t_id": self.kwargs['t_id'], "st_id": self.kwargs['st_id'], "test_id": self.kwargs['test_id'], "q_id": self.kwargs['q_id'], "a_id": self.kwargs['a_id']}))

    def post(self, request, *args, **kwargs):
        answer = self.get_object()
        q_id = answer.question.id
        test_id = answer.question.test.id
        st_id = answer.question.test.subtheme.id
        t_id = answer.question.test.subtheme.theme.id
        answer.delete()
        return redirect(reverse('testquestion_view', kwargs={"t_id": t_id, "st_id": st_id, "test_id": test_id, "q_id": q_id}))


class TestRunView(RoleRequiredMixin, View):
    template_name = 'tests/run.html'
    required_roles = []  # Доступно всем авторизованным

    def get(self, request, *args, **kwargs):
        theme = get_object_or_404(Theme, id=kwargs['t_id'])
        subtheme = get_object_or_404(SubTheme, id=kwargs['st_id'])
        test = get_object_or_404(Test, id=kwargs['test_id'])

        return render(request, self.template_name, {"theme": theme, "subtheme": subtheme, "test": test})

    def post(self, request, *args, **kwargs):
        theme = get_object_or_404(Theme, id=kwargs['t_id'])
        subtheme = get_object_or_404(SubTheme, id=kwargs['st_id'])
        test = get_object_or_404(Test, id=kwargs['test_id'])
        
        # Получаем выбранные ответы
        selected_answers = []
        for key in self.request.POST.keys():
            if key.isdigit():
                answer_ids = self.request.POST.getlist(key)
                selected_answers.extend([int(aid) for aid in answer_ids])
        
        # Сохраняем результат теста
        result = Result.objects.create(user=request.user, test=test)
        
        # Сохраняем выбранные ответы
        for answer_id in selected_answers:
            try:
                answer = TestAnswerVariant.objects.get(id=answer_id)
                ResultItem.objects.create(result=result, answer=answer)
            except TestAnswerVariant.DoesNotExist:
                pass
        
        # Подсчитываем правильные и неправильные ответы
        correct_count = 0
        total_questions = test.questions.count()
        
        for question in test.questions.all():
            correct_answers = set(question.answers.filter(is_right=True).values_list('id', flat=True))
            selected_for_question = set(
                ResultItem.objects.filter(
                    result=result,
                    answer__question=question
                ).values_list('answer_id', flat=True)
            )
            if correct_answers == selected_for_question and len(correct_answers) > 0:
                correct_count += 1
        
        # Вычисляем процент
        percentage = (correct_count / total_questions * 100) if total_questions > 0 else 0
        
        return render(request, self.template_name, {
            "theme": theme,
            "subtheme": subtheme,
            "test": test,
            "show_answers": True,
            "selected_answers": selected_answers,
            "correct_count": correct_count,
            "total_questions": total_questions,
            "percentage": round(percentage, 1)
        })

