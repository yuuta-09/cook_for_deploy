from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from bs4 import BeautifulSoup

from .models import Recipe, Ingredient


User = get_user_model()


# Create your tests here.
class RecipeModelTestCase(TestCase):
    def setUp(self):
        # テスト用のユーザを作成
        self.user = User.objects.create_user(
            'testuser',
            'testuserpassword'
        )

        # テスト用のレシピを作成
        self.recipe = Recipe.objects.create(
            name='Test Recipe',
            description='This is a test recipe description.',
            user=self.user
        )

    def test_create_recipe_with_required_fields(self):
        """
        正しくモデルが保存される
        """
        recipe = Recipe.objects.get(pk=self.recipe.pk)
        self.assertEqual(recipe.name, self.recipe.name)
        self.assertEqual(recipe.description, self.recipe.description)
        self.assertEqual(recipe.user, self.user)
        self.assertIsInstance(recipe.posted_at, timezone.datetime)

    def test_recipe_str(self):
        """
        __str__メソッドがnameフィールドを返す
        """
        self.assertEqual(str(self.recipe), self.recipe.name)

    def test_recipe_deletion(self):
        """
        レシピの削除が正しく動作する
        """
        self.recipe.delete()
        self.assertEqual(Recipe.objects.count(), 0)

    def test_create_recipe_without_name(self):
        """
        nameフィールドが必須である
        """
        recipe = Recipe(
            description='Description without name',
            user=self.user
        )
        with self.assertRaises(ValidationError):
            recipe.full_clean()

    def test_create_recipe_without_description(self):
        """
        descriptionフィールドが必須である
        """
        recipe = Recipe(
            name='Recipe without description',
            user=self.user
        )
        with self.assertRaises(ValidationError):
            recipe.full_clean()

    def test_create_recipe_without_user(self):
        """
        userフィールドが必須である
        """
        recipe = Recipe(
            name='Recipw without user',
            description='Description without user'
        )
        with self.assertRaises(ValidationError):
            recipe.full_clean()


class IngredientModelTestCase(TestCase):
    def setUp(self):
        # テスト用のユーザを作成
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )

        # テスト用のレシピを作成
        self.recipe = Recipe.objects.create(
            name='Test Recipe',
            description='This is a test recipe description',
            user=self.user
        )

        # テスト用の材料を作成
        self.ingredient = Ingredient.objects.create(
            name='Sugar',
            amount='100g',
            recipe=self.recipe
        )

    def test_ingredient_creation(self):
        """
        正しくモデルが保存される
        """
        ingredient = Ingredient.objects.get(pk=self.ingredient.pk)
        self.assertEqual(ingredient.name, self.ingredient.name)
        self.assertEqual(ingredient.amount, self.ingredient.amount)
        self.assertEqual(ingredient.recipe, self.recipe)

    def test_ingredient_str(self):
        """
        __str__メソッドがnameフィールドを返す
        """
        self.assertEqual(str(self.ingredient), self.ingredient.name)

    def test_ingredient_deletion(self):
        """
        材料が正しく削除できる
        """
        self.ingredient.delete()
        self.assertEqual(Ingredient.objects.count(), 0)

    def test_name_is_required(self):
        """
        nameフィールドが必須である
        """
        ingredient = Ingredient(
            amount='100g',
            recipe=self.recipe
        )
        with self.assertRaises(ValidationError):
            ingredient.full_clean()

    def test_amount_is_required(self):
        """
        amountフィールドが必須である
        """
        ingredient = Ingredient(
            name='Salt',
            recipe=self.recipe
        )
        with self.assertRaises(ValidationError):
            ingredient.full_clean()

    def test_recipe_is_required(self):
        ingredient = Ingredient(
            name='Salt',
            amount='50g'
        )
        with self.assertRaises(ValidationError):
            ingredient.full_clean()


class RecipeListViewTestCase(TestCase):
    list_link = reverse('cook:recipe_list')
    template_name = 'recipe/list.html'

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )

    def test_recipe_list_response(self):
        """
        urlが/recipesで一覧ページが表示される
        """
        response = self.client.get(self.list_link)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)

    def test_recipe_list_query_set_none(self):
        """
        一覧ページでまだ何も投稿されていないときに以下の条件を満たす
        ・query_setが空
        ・「まだレシピが登録されていません。」という文字がある
        """
        response = self.client.get(self.list_link)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertEqual(response.context['recipes'].count(), 0)
        self.assertContains(response, 'まだレシピが登録されていません。')

    def test_recipe_list_query_set_one(self):
        """
        一覧ページで1つ投稿されているときに以下の条件を満たす
        ・query_setの数が1
        ・1つのモデルのnameとdescriptionが表示されている
        ・1つのモデルの詳細ページへのリンクが存在する
        """
        recipe = Recipe.objects.create(
            name='test',
            description='name',
            user=self.user
        )

        response = self.client.get(self.list_link)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertEqual(response.context['recipes'].count(), 1)
        self.assertContains(response, recipe.name)
        self.assertContains(response, recipe.description)

        # BeautifulSoupを使ってレスポンスのHTMLをパース
        soup = BeautifulSoup(response.content, 'html.parser')

        # 特定のaタグを検索して、hrefとclassを確認
        recipe_link = reverse(
            'cook:recipe_detail', kwargs={'recipe_id': recipe.id}
        )
        exist_link = soup.find('a', href=recipe_link)
        self.assertIsNotNone(exist_link)

    def test_recipe_list_pagination(self):
        """
        ページネーションが存在し、1ページに最大5つのレシピが表示される
        それ以上の場合は次のページに表示される
        """
        for i in range(8):
            Recipe.objects.create(
                name=f'Recipe {i+1}',
                description=f'Description {i+1}',
                user=self.user
            )

        # 1ページ目の確認
        response = self.client.get(self.list_link)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['recipes'].count(), 5)
        # 次のページが存在しているか
        self.assertContains(response, 'href="?page=2"')

        # 2ページ目の確認
        response = self.client.get(self.list_link + '?page=2')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['recipes'].count(), 3)
        # 次のページへのリンクがないことを確認
        self.assertNotContains(response, 'href="?page=3"')


class ResipeDetailViewTestCase(TestCase):
    template_name = 'recipe/detail.html'

    def setUp(self):
        self.user_password = 'testpassword'
        self.user = User.objects.create_user(
            username='testuser',
            password=self.user_password
        )

        self.recipe = Recipe.objects.create(
            name='test recipe',
            description='This is a test recipe',
            user=self.user
        )

    def _get_description_url(self, recipe_id):
        return reverse('cook:recipe_detail', kwargs={'recipe_id': recipe_id})

    def _login_user(self, user, password):
        """
        ログイン処理を共通化
        """
        return self.client.login(username=user.username, password=password)

    def _login_other_user(self):
        """
        別ユーザでのログイン処理を共通化
        """
        other_password = 'other_user_password'
        other_user = User.objects.create_user(
            username='other_user',
            password=other_password
        )
        return self._login_user(other_user, other_password)

    def _assert_recipe_detail_page(self, response, user_can_edit=False):
        """
        レシピ詳細ページに表示される内容のassertを共通化
        """
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        # recipeの名前が表示される
        self.assertContains(response, self.recipe.name)
        # recipeの投稿者が表示される
        self.assertContains(response, self.recipe.user.username)
        # recipeの詳細が表示される
        self.assertContains(response, self.recipe.description)

        # リンクの存在確認
        soup = BeautifulSoup(response.content, 'html.parser')

        recipe_edit_link = reverse(
            'cook:recipe_edit', kwargs={'recipe_id': self.recipe.id}
        )
        recipe_edit_link_tag = soup.find('a', href=recipe_edit_link)

        recipe_destroy_link = reverse(
            'cook:recipe_destroy', kwargs={'recipe_id': self.recipe.id}
        )
        recipe_destroy_link_tag = soup.find(
            'form', action=recipe_destroy_link, method="post"
        )

        ingredient_new_link = reverse('cook:ingredient_new', kwargs={
                                      'recipe_id': self.recipe.id})
        ingredient_new_link_tag = soup.find('a', href=ingredient_new_link)

        if user_can_edit:
            self.assertIsNotNone(recipe_edit_link_tag)
            self.assertIsNotNone(recipe_destroy_link_tag)
            self.assertIsNotNone(ingredient_new_link_tag)
        else:
            self.assertIsNone(recipe_edit_link_tag)
            self.assertIsNone(recipe_destroy_link_tag)
            self.assertIsNone(ingredient_new_link_tag)

    def _create_ingredients(self):
        for i in range(10):
            Ingredient.objects.create(
                name=f'ingredient{i}',
                amount=f'{i*100}g',
                recipe=self.recipe
            )

    def _assert_ingredient(self, response, user_can_edit):
        soup = BeautifulSoup(response.content, 'html.parser')
        for ingredient in self.recipe.ingredients.all():
            self.assertContains(response, ingredient.name)
            self.assertContains(response, ingredient.amount)

            ingredient_edit_link = reverse(
                'cook:ingredient_edit',
                kwargs={'ingredient_id': ingredient.id}
            )
            ingredient_edit_link_tag = soup.find(
                'a', href=ingredient_edit_link
            )

            ingredient_destroy_link = reverse(
                'cook:ingredient_destroy',
                kwargs={'ingredient_id': ingredient.id}
            )
            ingredient_destroy_link_tag = soup.find(
                'form', action=ingredient_destroy_link, method="post"
            )

            if user_can_edit:
                self.assertIsNotNone(ingredient_edit_link_tag)
                self.assertIsNotNone(ingredient_destroy_link_tag)
            else:
                self.assertIsNone(ingredient_edit_link_tag)
                self.assertIsNone(ingredient_destroy_link_tag)

    def test_recipe_detail_response(self):
        """
        url(/cook/recipes/<int:recipe_id>/で詳細ページへ移動できる
        """
        response = self.client.get(self._get_description_url(self.recipe.id))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)

    def test_recipe_detail_response_with_not_exist(self):
        """
        存在しないレシピのページに移動したときに404エラーを返す
        """
        response = self.client.get(
            self._get_description_url(self.recipe.id+100)
        )
        self.assertEqual(response.status_code, 404)

    def test_recipe_detail_template_with_author(self):
        """
        存在するレシピのページに移動したときに表示される内容が正しい
        ログイン中のユーザと投稿者が同じ場合
        """
        self._login_user(self.user, self.user_password)
        response = self.client.get(self._get_description_url(self.recipe.id))
        self._assert_recipe_detail_page(response, user_can_edit=True)

    def test_recipe_detail_template_with_other_user(self):
        """
        存在するレシピのページに移動したときに表示される内容が正しい
        ログイン中のユーザと投稿者が違う場合
        """
        self._login_other_user()

        response = self.client.get(self._get_description_url(self.recipe.id))
        self._assert_recipe_detail_page(response, user_can_edit=False)

    def test_recipe_detail_template_without_user(self):
        """
        存在するレシピのページに移動したときに表示される内容が正しい
        ログインしていない場合
        """
        response = self.client.get(self._get_description_url(self.recipe.id))
        self._assert_recipe_detail_page(response, user_can_edit=False)

    def test_recipe_detail_ingredient_template_with_author(self):
        """
        存在するレシピのページに移動したときに表示される内容が正しい
        ログインしていた場合の材料の表示
        """
        self._create_ingredients()
        self._login_user(self.user, self.user_password)

        response = self.client.get(self._get_description_url(self.recipe.id))
        self._assert_ingredient(response, True)

    def test_recipe_detail_ingredient_template_with_other(self):
        """
        存在するレシピのページに移動したときに表示される内容が正しい
        投稿者とログインユーザが違う場合の材料の表示
        """
        self._create_ingredients()
        self._login_other_user()

        response = self.client.get(self._get_description_url(self.recipe.id))
        self._assert_ingredient(response, False)

    def test_recipe_detail_ingredient_template_without_user(self):
        """
        存在するレシピのページに移動したときに表示される内容が正しい
        ログインしていない場合の材料の表示が正しい
        """
        self._create_ingredients()
        response = self.client.get(self._get_description_url(self.recipe.id))
        self._assert_ingredient(response, False)


class RecipeCreateViewTestCase(TestCase):
    template_name = 'recipe/new.html'
    create_link = reverse('cook:recipe_new')

    def setUp(self):
        self.password = 'testpassword'
        self.user = User.objects.create_user(
            username='testuser',
            password=self.password
        )

    def test_recipe_creation_page_with_logged_in(self):
        """
        ログインしていれば新規投稿ページに移動できる
        """
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(self.create_link)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)

    def test_recipe_creation_page_required_logged_in(self):
        """
        新規投稿ページに移動した際、ログインしていなければログインページにリダイレクトする
        """
        response = self.client.get(self.create_link)
        self.assertRedirects(
            response, f"{reverse('account_login')}?next=/cook/recipes/new/"
        )

    def test_create_required_logged_in(self):
        """
        投稿時にログインしていなければログインページにリダイレクトする
        """
        post_data = {
            'name': 'New Recipe',
            'description': 'New recipe description'
        }
        response = self.client.post(self.create_link, post_data)
        self.assertRedirects(
            response, f"{reverse('account_login')}?next=/cook/recipes/new/"
        )

    def test_recipe_create_success(self):
        """
        投稿に成功した場合のテスト
        データの数が増える
        詳細ページにリダイレクトする
        """
        post_data = {
            'name': 'New Recipe',
            'description': 'New recipe description'
        }
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.post(self.create_link, post_data)
        self.assertEqual(Recipe.objects.count(), 1)
        self.assertRedirects(response, reverse('cook:recipe_list'))

    def test_recipe_failed_name_is_blank(self):
        """
        投稿に失敗した場合のテスト(nameが空)
        データの数が変わらない
        新規投稿ページに戻る
        バリデーションエラーが表示される
        """
        post_data = {
            'name': '',
            'description': 'New recipe description'
        }

        self.client.login(username=self.user.username, password=self.password)
        response = self.client.post(self.create_link, post_data)
        self.assertEqual(Recipe.objects.count(), 0)
        self.assertEqual(response.status_code, 200)  # フォームにエラーがあるため再表示される
        self.assertTemplateUsed(response, self.template_name)
        self.assertContains(response, 'このフィールドは必須です。')

    def test_recipe_fialed_description_is_blank(self):
        """
        投稿に失敗した場合のテスト(descriptionが空)
        """
        post_data = {
            'name': 'test recipe',
            'description': ''
        }

        self.client.login(username=self.user.username, password=self.password)
        response = self.client.post(self.create_link, post_data)
        self.assertEqual(Recipe.objects.count(), 0)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertContains(response, 'このフィールドは必須です。')


class RecipeUpdateViewTestCase(TestCase):
    template_name = 'recipe/edit.html'
    update_data = {
        'name': 'updated_name',
        'description': 'updated_description'
    }

    def setUp(self):
        self.password = 'testpassword'
        self.user = User.objects.create_user(
            username='testuser',
            password=self.password
        )

        self.recipe = Recipe.objects.create(
            name='test_recipe',
            description='This is a test recipe',
            user=self.user
        )

    def _get_update_link(self, recipe_id):
        return reverse(
            'cook:recipe_edit', kwargs={'recipe_id': recipe_id}
        )

    def _login_user(self):
        self.client.login(username=self.user.username, password=self.password)

    def _create_error_update_data(self, name, description):
        return {
            'name': name,
            'description': description
        }

    def _login_other_user(self):
        user = User.objects.create_user(
            username='otheruser',
            password='otherpassword'
        )
        self.client.login(username=user.username, password='otherpassword')

    def test_recipe_update_page_with_correct_user(self):
        """
        ログインしているユーザが投稿者の場合は更新ページへ移動できる
        """
        self._login_user()
        response = self.client.get(self._get_update_link(self.recipe.id))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)

    def test_recipe_update_page_with_uncorrect_user(self):
        """
        ログインしているユーザが投稿者でない場合は403エラーが返る
        """
        self._login_other_user()
        response = self.client.get(self._get_update_link(self.recipe.id))
        self.assertEqual(response.status_code, 403)

    def test_recipe_update_page_without_logged_in(self):
        """
        ログインしていない場合はログインページへリダイレクトする
        """
        response = self.client.get(self._get_update_link(self.recipe.id))

        login_link = reverse('account_login')
        next_link = self._get_update_link(self.recipe.id)
        redirect_url = f'{login_link}?next={next_link}'

        self.assertRedirects(response, redirect_url)

    def test_recipe_update_required_logged_in(self):
        """
        ログインせずに更新を行おうとした場合はログインページへ移動する
        """
        response = self.client.post(
            self._get_update_link(self.recipe.id), self.update_data
        )

        login_link = reverse('account_login')
        next_link = self._get_update_link(self.recipe.id)
        redirect_url = f'{login_link}?next={next_link}'

        self.assertRedirects(response, redirect_url)

    def test_recipe_update_another_user(self):
        """
        ログインしているが、投稿者とログイン中のユーザが異なる場合
        403エラーが発生する。
        """
        self._login_other_user()
        response = self.client.post(
            self._get_update_link(self.recipe.id), self.update_data
        )

        self.assertEqual(response.status_code, 403)

    def test_recipe_update_success(self):
        """
        ログインしていてかつ投稿者とログイン中のユーザが一致する場合は更新に成功する
        成功した場合はrecipeの詳細ページへ移動する
        """
        self._login_user()
        response = self.client.post(
            self._get_update_link(self.recipe.id), self.update_data
        )

        updated_recipe = Recipe.objects.get(pk=self.recipe.id)
        self.assertEqual(updated_recipe.name, self.update_data['name'])
        self.assertEqual(
            updated_recipe.description, self.update_data['description']
        )
        self.assertRedirects(
            response,
            reverse('cook:recipe_detail', kwargs={'recipe_id': self.recipe.id})
        )

    def test_recipe_update_failed_name_is_blank(self):
        """
        ログインしていてかつ投稿者とログイン中のユーザが一致していてnameが空の場合
        recipeのupdateページに戻る
        バリデーションエラーが表示される
        """
        self._login_user()
        update_data = self._create_error_update_data('', 'updated_description')
        response = self.client.post(
            self._get_update_link(self.recipe.id), update_data
        )

        self.assertEqual(response.status_code, 200)  # バリデーションエラーがあるため再描画される
        self.assertTemplateUsed(response, self.template_name)
        self.assertContains(response, 'このフィールドは必須です。')

    def test_recipe_update_failed_description_is_blank(self):
        """
        ログインしていてかつ投稿者とログイン中のユーザが一致していてdescriptionが空の場合
        recipeのupdateページに戻る
        バリデーションエラーが表示される
        """
        self._login_user()
        update_data = self._create_error_update_data('updated_name', '')
        response = self.client.post(
            self._get_update_link(self.recipe.id), update_data
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)
        self.assertContains(response, 'このフィールドは必須です')


class RecipeDeleteViewTestCase(TestCase):
    def setUp(self):
        self.password = 'testpassword'
        self.user = User.objects.create_user(
            username='testuser',
            password=self.password
        )

        self.recipe = Recipe.objects.create(
            name='testrecipe',
            description='This is the test recipe.',
            user=self.user
        )

        self.ingredient = Ingredient.objects.create(
            name='testingredient',
            amount='100g',
            recipe=self.recipe
        )

    def _login_user(self):
        self.client.login(username=self.user.username, password=self.password)

    def _login_other_user(self):
        other_user = User.objects.create_user(
            username='otheruser',
            password='otherpassword'
        )

        self.client.login(
            username=other_user.username, password='otherpassword'
        )

    def _get_destroy_link(self, recipe_id):
        return reverse(
            'cook:recipe_destroy',
            kwargs={'recipe_id': recipe_id}
        )

    def test_delete_correct_user(self):
        """
        以下の場合に削除ができる
        ログイン中のユーザと投稿をしたユーザが一致した場合
        urlが/cook/recipes/<int: recipe_id > /destroy/
        HTTPメソッドがPOST
        """
        self._login_user()
        response = self.client.post(self._get_destroy_link(self.recipe.id))

        self.assertRedirects(response, reverse('cook:recipe_list'))

        self.assertFalse(Recipe.objects.filter(id=self.recipe.id).exists())
        # models.CASCADEのチェック
        self.assertFalse(
            Ingredient.objects.filter(recipe=self.recipe).exists()
        )

    def test_delete_another_user(self):
        """
        ログイン中のユーザと投稿を行ったユーザが一致しない場合削除に失敗する
        403 Forbiddenが返る
        """
        self._login_other_user()
        response = self.client.post(self._get_destroy_link(self.recipe.id))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Recipe.objects.filter(id=self.recipe.id).exists())

    def test_delete_without_logged_in(self):
        """
        ログインをしていない場合にはログインページへリダイレクトする。
        """
        response = self.client.post(self._get_destroy_link(self.recipe.id))

        login_url = reverse('account_login')
        next_url = self._get_destroy_link(self.recipe.id)
        redirect_url = f'{login_url}?next={next_url}'

        self.assertRedirects(response, redirect_url)
        self.assertTrue(Recipe.objects.filter(id=self.recipe.id).exists())

    def test_delete_with_http_get(self):
        """
        urlが/cook/recipes/<int: recipe_id > /destroy/
        HTTPメソッドがGETだったら404 Not Foundが返る
        """
        self._login_user()
        response = self.client.get(self._get_destroy_link(self.recipe.id))

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')
        self.assertTrue(Recipe.objects.filter(id=self.recipe.id).exists())


class IngredientCreateViewTestCase(TestCase):
    def test_ingredient_creation_page_with_correct_user(self):
        """
        レシピを投稿した人とログイン中のユーザが正しい場合
        材料の新規投稿フォームが正しく表示される
        """
        pass

    def test_ingredient_creation_page_with_another_user(self):
        """
        レシピを投稿した人とログイン中のユーザが異なる場合
        レシピの詳細ページへリダイレクトする。
        """
        pass

    def test_ingredient_creation_page_without_logged_in(self):
        """
        ログインせずに材料の新規投稿ページへ遷移しようとした場合
        ログインページにリダイレクトする
        """
        pass


class IngredientEditViewTestCase(TestCase):
    pass


class IngredientDeleteViewTestCase(TestCase):
    pass
