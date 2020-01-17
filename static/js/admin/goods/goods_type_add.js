$(function () {

  // 获取缩略图输入框元素
  let $thumbnailUrl = $("#news-thumbnail-url");

  // ================== 上传图片文件至服务器 ================
  let $upload_to_server = $("#upload-news-thumbnail");
  $upload_to_server.change(function () {
    let file = this.files[0];   // 获取文件
    let oFormData = new FormData();  // 创建一个 FormData
    oFormData.append("image_file", file); // 把文件添加进去
    // 发送请求
    $.ajax({
      url: "/admin/goods/images/",
      method: "POST",
      data: oFormData,
      processData: false,   // 定义文件的传输
      contentType: false,
    })
      .done(function (res) {
        if (res.errno === "0") {
          // 更新标签成功
          message.showSuccess("图片上传成功");
          let sImageUrl = res["data"]["image_url"];
          // console.log(thumbnailUrl);
          $thumbnailUrl.val('');
          $thumbnailUrl.val(sImageUrl);
          $("#type-image").attr('src', sImageUrl)
        } else {
          message.showError(res.errmsg)
        }
      })
      .fail(function () {
        message.showError('服务器超时，请重试！');
      });

  });


  // ================== 添加商品类型 ================
  let $newsBtn = $("#btn-add-type");
  $newsBtn.click(function () {
    // 判断文章标题是否为空
    let sTitle = $("#type-title").val();
    if (!sTitle) {
        message.showError('请填写商品类型名称！');
        return
    }
    // 判断文章摘要是否为空
    let sLogo = $("#type-logo").val();
    if (!sLogo) {
        message.showError('请填写商品类型logo！');
        return
    }


    let sThumbnailUrl = $thumbnailUrl.val();
    if (!sThumbnailUrl) {
      message.showError('请上传商品类型图');
      return
    }

    // 获取news_id 存在表示更新 不存在表示发表
    let newsId = $(this).data("news-id");
    let url = newsId ? '/admin/goods_type/edit/' + newsId + '/' : '/admin/goods_type/add/';
    let data = {
      "title": sTitle,
      "logo": sLogo,
      "image_url": sThumbnailUrl,
    };

    $.ajax({
      // 请求地址
      url: url,
      // 请求方式
      type: newsId ? 'PUT' : 'POST',
      data: JSON.stringify(data),
      // 请求内容的数据类型（前端发给后端的格式）
      contentType: "application/json; charset=utf-8",
      // 响应数据的格式（后端返回给前端的格式）
      dataType: "json",
    })
      .done(function (res) {
        if (res.errno === "0") {
          if (newsId) {
              message.showSuccess("商品类型更新成功");
              setTimeout(function () {
                window.location.href='http://127.0.0.1:8000/admin/goods_type/';
                }, 1000)

          } else {
              message.showSuccess("商品类型添加成功");
              setTimeout(function () {
                window.location.href='http://127.0.0.1:8000/admin/goods_type/';
                }, 1000)
          }
        } else {
          fAlert.alertErrorToast(res.errmsg);
        }
      })
      .fail(function () {
        message.showError('服务器超时，请重试！');
      });
  });


  // get cookie using jQuery
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      let cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        let cookie = jQuery.trim(cookies[i]);
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
  }

  // Setting the token on the AJAX request
  $.ajaxSetup({
    beforeSend: function (xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
      }
    }
  });

});
