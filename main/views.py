from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from main.forms import SubThemeForm
from main.models import Theme, SubTheme, Article, Test, TestQuestion, TestAnswerVariant


def index_page(request):
    return render(request, "index.html")


class ThemeBaseMixin:
    model = Theme
    pk_url_kwarg = 'id'
    fields = ["title"]


class ThemeListView(ThemeBaseMixin, ListView):
    template_name = 'themes/list.html'


class ThemeDetailView(ThemeBaseMixin, DetailView):
    template_name = 'themes/view.html'


class ThemeAddView(ThemeBaseMixin, CreateView):
    template_name = 'themes/add.html'


class ThemeEditView(ThemeBaseMixin, UpdateView):
    template_name = 'themes/edit.html'


class ThemeDeleteView(ThemeBaseMixin, DeleteView):
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


class SubThemeDetailView(SubThemeBaseMixin, DetailView):
    template_name = 'subthemes/view.html'


class SubThemeUpdateView(SubThemeBaseMixin, UpdateView):
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


class SubThemeCreateView(SubThemeBaseMixin, CreateView):
    template_name = 'subthemes/add.html'

    def form_valid(self, form):
        return self.get_success_redirect(self.save_subtheme_and_article(form))


class SubThemeDeleteView(SubThemeBaseMixin, DeleteView):
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


class TestListView(TestBaseMixin, ListView):
    template_name = 'tests/list.html'

    def get_queryset(self):
        return Test.objects.filter(subtheme_id=self.kwargs['st_id']).select_related('subtheme', 'subtheme__theme')


class TestDetailView(TestBaseMixin, DetailView):
    template_name = 'tests/view.html'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('questions__answers')


class TestCreateView(TestBaseMixin, CreateView):
    template_name = 'tests/add.html'

    def form_valid(self, form):
        test = form.save(commit=False)
        test.subtheme = self.get_subtheme()
        test.save()
        return self.get_success_redirect(test)


class TestUpdateView(TestBaseMixin, UpdateView):
    template_name = 'tests/edit.html'

    def form_valid(self, form):
        return self.get_success_redirect(form.save())


class TestDeleteView(TestBaseMixin, DeleteView):
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


class TestQuestionDetailView(TestQuestionBaseMixin, DetailView):
    template_name = 'testquestions/view.html'


class TestQuestionCreateView(TestQuestionBaseMixin, CreateView):
    template_name = 'testquestions/add.html'

    def form_valid(self, form):
        question = form.save(commit=False)
        question.test = self.get_test()
        question.save()
        return self.get_success_redirect(question)


class TestQuestionUpdateView(TestQuestionBaseMixin, UpdateView):
    template_name = 'testquestions/edit.html'

    def form_valid(self, form):
        return self.get_success_redirect(form.save())


class TestQuestionDeleteView(TestQuestionBaseMixin, DeleteView):
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


class TestAnswerVariantDetailView(TestAnswerVariantBaseMixin, DetailView):
    template_name = 'testanswervariants/view.html'


class TestAnswerVariantCreateView(TestAnswerVariantBaseMixin, CreateView):
    template_name = 'testanswervariants/add.html'

    def form_valid(self, form):
        answer = form.save(commit=False)
        answer.question = self.get_question()
        answer.save()
        return self.get_success_redirect(answer)


class TestAnswerVariantUpdateView(TestAnswerVariantBaseMixin, UpdateView):
    template_name = 'testanswervariants/edit.html'

    def form_valid(self, form):
        return self.get_success_redirect(form.save())


class TestAnswerVariantDeleteView(TestAnswerVariantBaseMixin, DeleteView):
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


class TestRunView (View):

    template_name = 'tests/run.html'

    def get(self, request, *args, **kwargs):
        theme = get_object_or_404(Theme, id=kwargs['t_id'])
        subtheme = get_object_or_404(SubTheme, id=kwargs['st_id'])
        test = get_object_or_404(Test, id=kwargs['test_id'])

        return render(request, self.template_name,  {"theme": theme, "subtheme": subtheme, "test": test})

    def post(self, request, *args, **kwargs):
        theme = get_object_or_404(Theme, id=kwargs['t_id'])
        subtheme = get_object_or_404(SubTheme, id=kwargs['st_id'])
        test = get_object_or_404(Test, id=kwargs['test_id'])
        print(self.request.POST)

        answers = []
        for k in self.request.POST.keys():
            print(k)
            if k.isdigit():
                v = self.request.POST.getlist(k)
                answers += [int(item) for item in v ]

        print(answers)
        return render(request, self.template_name, {"theme": theme, "subtheme": subtheme, "test": test, "show_answers": True, "answers": answers})

