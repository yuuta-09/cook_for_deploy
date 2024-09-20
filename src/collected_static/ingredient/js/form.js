$(document).ready(function() {
  $("button[name=remove_form]").click(function(event) {
    console.log('started remove_form');
    // id_ingredients-TOTAL_FORMSというidのinputのデータを取得する
    const totalFormsInput = parseInt($("#id_ingredients-TOTAL_FORMS").val());
    const lastFormsNumber = totalFormsInput - 1;

    // 取得した番号のフォームの中に値が入力されていた場合
    const inputFieldVal = $(`#id_ingredients-${lastFormsNumber}-name`).val().trim();
    const textFieldVal = $(`#id_ingredients-${lastFormsNumber}-amount`).val().trim();

    if (inputFieldVal || textFieldVal) {
      const result = confirm(
        `以下のフォームの内容が削除されますがよろしいですか？\n材料名: ${inputFieldVal}\n量: ${textFieldVal}`
      );
      if (!result) {
        event.preventDefault(); // フォームの送信を中止
      }
    }

    this.off('hover');
  })

  $("button[name=reset_form]").click(function(event) {
    // 現在入力されている値はすべて消去されるがよいかを確認。
    if (!confirm("現在入力されている値はすべて消去されますが、よろしいですか？")) {
      event.preventDefault(); // フォームの送信を中止
    }

  });
});
