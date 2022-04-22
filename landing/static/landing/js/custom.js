$(document).ready(function () {
    let imageString;
    let cropX;
    let cropY;
    let cropWidth;
    let cropHeight;
    let max_size;
    let imageFiles = []
    const modalsId = ["#CreatePostModal", "#UpdatePostModal"]

    $("button[data-bs-dismiss='modal']").on("click", (e) => {
        var form = $(e.target).parent().parent().find(".modal-body").find("form");
        form.length !== 0 ? $(form)[0].reset() : "";
        $("#PreviewImagesContainer").html("")
    });
    $("#CreatePostModal").on("keyup", (e) => {
        if (e.target.tagName !== "INPUT" && e.target.tagName !== "TEXTAREA") return;
        if (e.target.classList.contains("is-invalid")) {
            e.target.classList.remove("is-invalid");
        }
    })
    modalsId.forEach((_id, index) => {
        $(`${_id}`).on("click", (e) => {
            if ($(e.target).attr("id") !== "createPostBtn") return;
            e.preventDefault();
            $(e.target.nextElementSibling).fadeIn()
            e.target.setAttribute("disabled", true);
            var form = $(`${_id} #createPostForm`)[0]
            var data = new FormData(form);

            for (var i = 0; i < imageFiles.length; i++) { // append the uuploaded images to data
                data.append('images', imageFiles[i]);
            };

            $.ajax({
                url: $(`${_id}`).attr("data-url"),
                data: data, //$("#CreatePostModal #createPostForm").serialize(),
                method: "post",
                processData: false,
                cache: false,
                contentType: false,
                dataType: "json",
                success: (data) => {
                    if (data.success) {
                        let message;
                        setTimeout(() => {
                            $(e.target).next().fadeOut("slow");
                            // take care of the reset form for both later
                            ResetForm('createPostForm', 'PreviewImagesContainer')
                            $(`${_id}`).modal('hide');
                            $(e.target.nextElementSibling).fadeOut("slow")
                            _id === "#UpdatePostModal" ? message = "Post has been updated" :
                                message = "Post has been created"
                            alertUser(`${message}`, "successfully!")// alerting the user 
                            UpdatePostUI(_id, data.template, data.post_slug)
                        }, 1000)

                    } else {
                        $(`${_id} #createPostForm`).replaceWith(data.formErrors);
                        $(`${_id} .PreviewImagesContainer`).html("");
                        $(`${_id}`).find("form").attr("id", "createPostForm");
                        $(e.target.nextElementSibling).fadeOut("slow")
                    };

                    $(e.target).prop("disabled", false);
                },
                error: (error) => {
                    console.log(error)
                }
            })
        });

    })

    modalsId.forEach((_id, index) => {
        $(`${_id}`).on("change", (e) => {
            if ($(e.target).attr("id") !== "id_images") return;
            var postImagesPreviewContainer = document.querySelector(`${_id} .PreviewImagesContainer`);
            $(`${_id} .maxFileError`).fadeOut()
            $(postImagesPreviewContainer).html("");
            if ($(e.target.files.length) > 5) {
                $(`${_id} .maxFileError`).fadeIn()
                return;
            }

            var row = document.createElement("div")
            row.setAttribute("class", "post-images")
            var second_child_row = document.createElement("div")
            var first_child_row = document.createElement("div")
            $(row).append(first_child_row).append(second_child_row)

            Array.from(e.target.files).forEach((file, i) => {
                const postImageChild = document.createElement("div");
                postImageChild.setAttribute("class", "post-images__child")
                const reader = new FileReader();
                reader.onload = () => {
                    img = document.createElement("img")
                    img.setAttribute("src", reader.result)

                    img.onload = (e) => {
                        // here i will process on resizing the image
                        const canvas = document.createElement("canvas")
                        const max_width = 680
                        const scaleSize = max_width / e.target.width
                        canvas.width = max_width
                        canvas.height = e.target.height * scaleSize
                        var ctx = canvas.getContext("2d") // setting the context of the canvas
                        ctx.drawImage(e.target, 0, 0, canvas.width, canvas.height)
                        const encodedSource = ctx.canvas.toDataURL(e.target, 'image/png', 1)
                        const processedImg = document.createElement("img") // create a processed image and return it.
                        processedImg.src = encodedSource
                        $(postImageChild).append(processedImg)
                        imageFiles.splice(0, imageFiles.length) // clear all the images before adding the new ones
                        imageFiles.push(processedImg)
                    }
                }
                (i === 2 | i === 4) ?
                    $(first_child_row).append(postImageChild)
                    : $(second_child_row).append(postImageChild)

                $(postImagesPreviewContainer).append(row);
                reader.readAsDataURL(file)
                var image_input_div = document.querySelector(`${_id} #createPostForm #div_id_images`);
                document.querySelector(`${_id} #createPostForm`).insertBefore(postImagesPreviewContainer, image_input_div)
            });
        })
    })

    // ################ Events listeners here ###################
    $(".posts-section").on("click", (e) => {
        console.log(e.target.classList, "this is the class list")
        if (!(e.target.href) && !(e.target.name)) return;
        if (e.target.href) {
            if ((e.target.href).split("/").at(-1) === "#UpdatePostModal") return GetUpdatePost(e);
            if ((e.target.href).split("/").at(-1) === "#DeletePostModal") return DeletePost(e);
            if ((e.target.href).split("/").at(-1) === "#DeleteCommentPostModal") return DeleteCommentPost(e);
        } else {
            if (e.target.getAttribute("name") === "PostLike") return PostLike(e);
            if (e.target.getAttribute("name") === "commentpost") return commentOnPost(e);

        }
    });
    $(".user_profile").on("click", (e) => {
        if (e.target.href) return editUserProfile(e);
        if ((e.target.name) && !(e.target.href)) return FollowUnfollowProfile(e);

    })

    $("#user_profile").on("click", (e) => { editUserProfile(e) });

    $("#forge_link_status").on("click", (e) => {
        if ($(e.target).attr('id') === "ForgeNewLink") return ForgeNewLink(e);
        if ($(e.target).attr('id') === "CancelLinkForge") return cancelForgeLink(e);
    });
    $("[data-role='AcceptForgeLink']").on("click", (e) => {
        acceptLinkForge(e);
    });
    $("[data-role='DeleteForgeLink']").on("click", (e) => {
        deleteLinkForge(e);
    });

    $(".companies-list").on('click', (e) => {
        if (!($(e.target).attr("data-role"))) return;
        if ($(e.target).attr("data-role") === "ForgeNewLink") return ForgeNewLink(e);
        if ($(e.target).attr("data-role") === "CancelLinkForge") return cancelForgeLink(e);
        if ($(e.target).attr("data-role") === "DeleteForgeLink") return deleteLinkForge(e);
        if ($(e.target).attr("data-role") === "Disconnect") return unLink(e);
    })

    // #################### function sections here ################
    function setImageProperties(image, x, y, width, height) {
        imageString = image;
        cropX = x;
        cropY = y;
        cropWidth = width;
        cropHeight = height;
    }
    function CheckImageSize(image, max_upload_size) {
        var startIndex = image.indexOf("base64,") + 7
        var imageBase64 = image.substring(startIndex)
        var decodedImg = atob(imageBase64)
        if (decodedImg >= max_upload_size) {
            return null;
        } else {
            return imageBase64
        }
    }
    // the rolw of this function is to send the image as a string
    // since ajax cannot send image files
    function CropImage(image, cropX, cropY, cropWidth, cropHeight, max_upload_size, e) {
        //fisrt check if the size of the image is not greater than size allowed
        // in the settings.py file
        var imageString = CheckImageSize(image, max_upload_size);
        if (imageString !== null) {
            var data = {
                "imageString": imageString,
                "cropX": cropX,
                "cropY": cropY,
                "cropHeight": cropHeight,
                "cropWidth": cropWidth,
                "csrfmiddlewaretoken": csrftoken,
            }
            $.ajax({
                url: "/connection/cropping-image/",
                dataType: "json",
                method: "post",
                data: data,
                success: function (data) {
                    if (data.success) {
                        // updating the images places
                        var aside_pro_img = $(".user_profile .user-pro-img img")
                        $(aside_pro_img).attr("src", data.profile_url);
                        var nav_pro_img = $(".user-account .user-info img");
                        $(nav_pro_img).attr("src", data.profile_url);
                        // fade out the modal and reset the form
                        $("#UserProfileModal").modal("hide")
                        $("#UserProfileForm")[0].reset();
                        $(e.target).prop("disabled", false);
                        $(e.target.nextElementSibling).fadeOut()
                    } else {
                        alert(data.error)
                    }
                },
                error: function (error) {
                    console.log("error", error);
                },
            })

        } else {
            alert("Please Upload an image less than")
        }

    }
    function editUserProfile(e) {
        var profile_slug = window.location.pathname.split("/").at(-2)
        var url = `/connection/update-profile/${profile_slug}/`
        var loading_div = `
            div class="process-comm">
                <div class="spinner">
                <div class="bounce1"></div>
                <div class="bounce2"></div>
                <div class="bounce3"></div>
                </div>
            </div>
        `
        $("#UserProfileModal .modal-body .container-fluid").html(loading_div)
        if ((e.target.href) && (e.target.name)) {
            var target_name = $(e.target).attr("name");
            $.ajax({
                url: url,
                type: "get",
                success: function (data) {
                    if (!(data.error)) {
                        var modal_body = $("#UserProfileModal .modal-body .container-fluid")
                        $(modal_body).html(data.template)
                        max_size = data.max_size; // this  will be use to compare the image with allowed size from the settings.
                        $("#UserProfileForm").children().each((index, el) => {
                            if (el.tagName === "DIV" && !(($(el).attr("id")).includes(target_name))) {
                                $(el).addClass("d-none");
                                $("#UserProfileForm").removeClass("d-none");

                            }
                        })
                        if (target_name === "avatar") {
                            // creating programmatically the image preview div
                            var imageContainerDiv = $("<div/>", {
                                'id': 'ImageProfilePreview',
                                'class': 'container',
                                'style': 'font-weight:bold; color:black;',
                                'html': `<div style="align-text:center">
                                            <img id="prev_me" src="${data.profileUrl}" alt="Your current profile image" />
                                         </div>
                                        `,
                                // 'click': function () { alert(this.id) },
                            }).appendTo(modal_body);
                            // move this to its own function
                            $("#id_avatar").on("change", (e) => {
                                if (e.target.files[0]) {
                                    var reader = new FileReader();
                                    reader.onload = (e) => {
                                        imageSrc = e.target.result
                                        var imagePreview = document.getElementById("prev_me")
                                        imagePreview.src = imageSrc;
                                        cropper = new Cropper(imagePreview, {
                                            aspectRatio: 1 / 1,
                                            crop: function (e) {
                                                setImageProperties(imageSrc, e.detail.x, e.detail.y, e.detail.width, e.detail.height)
                                            }
                                        })
                                    }
                                    reader.readAsDataURL(e.target.files[0]);
                                }
                            });
                        }
                    } else {
                        alert(data.error)
                    }
                },
                error: function (error) {

                }
            })

        } else { return; }
        $("#UserProfileModal #UpdateProfileBtn").on("click", (e) => {
            $(e.target).attr("disabled", true);
            $(e.target.nextElementSibling).fadeIn()
            if ((target_name !== "avatar")) { // we handle the image update differently               
                var _form_data = $("#UserProfileForm").serialize()
                e.preventDefault();
                $.ajax({
                    url: url,
                    type: "post",
                    data: _form_data,
                    dataType: "json",
                    success: (data) => {
                        if (data.success) {
                            $("#UserProfileModal").modal("hide")
                            $("#UserProfileForm")[0].reset();
                            $(e.target).prop("disabled", false);
                            $(e.target.nextElementSibling).fadeOut()
                            // Update the UI
                            var span = $("#user_profile").find(`p.${data.field_name}`)
                            $(span).text(data.new_value)

                        }
                    },
                    error: (error) => {
                        console.log("this is an error", error)
                    }
                })
            } else {
                e.preventDefault()
                CropImage(imageString, cropX, cropY, cropWidth, cropHeight, max_size, e)
            }
        })
    }
    function FollowUnfollowProfile(e) {
        var target = $(e.target)
        var name = $(target).attr("name");
        var profile_slug = window.location.pathname.split("/").at(-2)
        var url = `/social/add-remove-follower/${profile_slug}/`
        $.ajax({
            url: url,
            method: "post",
            dataType: "json",
            data: {
                "data_name": name,
                "csrfmiddlewaretoken": csrftoken,
            },
            success: function (data) {
                if (data.success) {
                    let message;
                    var numb_of_flowing = $(".flw-status .followers").text();
                    console.log(numb_of_flowing, "nub of followers")
                    if (e.target.getAttribute("name") === "flww") {
                        message = "You are now following";
                        $(e.target).text("Unfollow");
                        $(e.target).attr("name", "unflww");
                        $(".flw-status .followers").text(parseInt(numb_of_flowing) + 1)
                    } else {
                        message = "You have been remove from the followers of"
                        $(e.target).text("Follow")
                        $(e.target).attr("name", "flww");
                        $(".flw-status .followers").text(parseInt(numb_of_flowing) - 1)
                    }
                    alertUser(`${message}`, `${data.following}`)
                    // update the btn and the number of following
                } else {
                    console.log(data.error)
                    alert(data.error)
                }
            },
            error: function (e) {
                console.log(e)
            }
        })

    }
    function alertUser(key, message) {
        alertify.set('notifier', 'position', 'top-right');
        alertify.set('notifier', 'delay', 7);
        alertify.success(`${key}  ${message}`);

    }
    function ResetForm(formId, imagePreviewId) {
        $("#" + formId)[0].reset()
        $("#" + imagePreviewId).html("")
    }
    function GetUpdatePost(e) {
        var loading = `
        <div class="PreviewImagesContainer">
            <div class="spinner">
                <div class="bounce1"></div>
                <div class="bounce2"></div>
                <div class="bounce3"></div>
            </div>
        </div>
    `
        $("#UpdatePostModal .modal-body .container-fluid").html(loading)
        var post_slug = e.target.id
        $("#UpdatePostModal").attr("data-url", `/social/post-update/${post_slug}/`)
        $.ajax({
            url: `/social/post-update/${post_slug}/`,
            type: "get",
            dataType: "json",
            success: function (data) {
                var updateFormLocal = $("#UpdatePostModal .modal-body .container-fluid")
                updateFormLocal.html(data.template);
                var _dataFiles = new DataTransfer();
                var images = document.querySelectorAll("#UpdatePostModal .post-images__child img")
                var image_input = $(updateFormLocal).find("#id_images")[0];
                images.forEach((img, index) => {
                    var _ImgName = img.currentSrc.split("/").at(-1)
                    // the srcToFile function will return a promise
                    // so we need to call the then method to get the result which is a file
                    async function insertImagesToFileInput() {
                        var file = await srcToFile2(img.currentSrc, _ImgName, "image/jpeg")
                        _dataFiles.items.add(file)
                        image_input.files = _dataFiles.files
                    }
                    insertImagesToFileInput();
                })



                var maxFileError = `
                <div class="maxFileError">
                    <p class="errornote">You cannot upload more than 5 images</p>
                </div>
            `
                updateFormLocal.append(maxFileError);
            },
            error: function (error) {
                console.log("there is an error for updating  this post", error);
            }

        })
    }
    function DeletePost(e) {

        $("#DeletePostModal").on("click", (ev) => {
            if ($(ev.target).attr("id") !== "deletePostBtn") return;
            ev.preventDefault();
            var post_slug = $(e.target).attr("data-slug")
            var url = `/social/post-delete/${post_slug}/`
            var _form = $("#deletePostForm")
            $.ajax({
                url: url,
                data: _form.serialize(),
                type: "post",
                dataType: "json",
                success: function (data) {
                    if (data.success) {
                        $(`#DeletePostModal`).modal('hide');
                        alertUser("Post", "has been deleted successfully");
                        $(".posts-section").find(`[data-slug=${post_slug}]`).fadeOut();
                    }
                },
                error: function (error) {
                    console.log("error", error)
                }
            })

        })

    }
    function commentOnPost(e) {
        e.preventDefault();
        e.target.setAttribute("disabled", "true");
        $(e.target.nextElementSibling).fadeIn()
        var _form = $(e.target).parent();
        var post_slug = _form.attr("data-slug");
        $.ajax({
            url: `/social/comment-on-post/${post_slug}/`,
            data: _form.serialize(),
            method: "post",
            success: function (data) {
                if (data.success) {
                    var comment = JSON.parse(data.comment_obj)
                    var date_commented = timeSince(comment[0].fields["date_commented"])
                    console.log("this is the date commented after js", date_commented)
                    var commentUl = `
                        <ul class="comment_instance_${comment[0].pk}">
                            <li>
                                <div class="comment-list">
                                    <div class="bg-img">
                                        <img src="${data.imageUrl}" style="width: 40px;" alt="">
                                    </div>
                                    <div class="comment"> 
                                        <h3>${comment[0].fields["author"][0]}</h3>
                                        <div> 
                                            <p>${comment[0].fields["content"]}</p>
                                        </div>
                                        <a href="#" title="" class="active"><i class="fa fa-reply-all"></i>Reply</a>
                                        <span style="display:inline;"><i class="fa fa-clock mx-1"></i></span>
                                        <span style="display:inline";> ${date_commented}</span>
                                        <button name="PostLike" data-slug="comment_like_${comment[0].fields['comment_slug']}" class="com-action com mx-0" style="padding: 1px 7px;">
                                            <i class="far fa-thumbs-up" style="pointer-events: none;"></i>
                                            <span class="likes-count" style="display:inline;pointer-events:none;">0</span>
                                        </button>
                                        <span id="comment_delete_${comment[0].pk}" class="com-action">
                                            <a data-bs-toggle="modal" data-slug="comment_${comment[0].pk}" href="#DeleteCommentPostModal"> 
                                                <i class="fa fa-trash mx-1"></i>
                                            </a>                               
                                        </span>
                                    </div>
                                </div >           
                            </li >
                        </ul >
                        `
                    var commentsContainer = $(`.post-comment-${post_slug}`)
                    if (commentsContainer.children().length === 1) {
                        var comment_section = document.createElement("div");
                        $(comment_section).attr("class", "comment-section");
                        var comment_sec = document.createElement("div");
                        $(comment_sec).attr("class", "comment-sec");
                        comment_section.appendChild(comment_sec);
                        $(comment_sec).append(commentUl)
                        $(commentsContainer).prepend(comment_section);
                    } else {
                        $(commentsContainer).find(".comment-sec").append(commentUl)
                    }
                    $(e.target).prop("disabled", false);
                    $(e.target.nextElementSibling).fadeOut("slow");
                    _form[0].reset();
                    var comments_count = $(`.${post_slug}_comments_count`).text()
                    $(`.${post_slug}_comments_count`).text(parseInt(comments_count) + 1)


                }
            },

            error: function (error) {
                console.log("there was an error when commenting on post", error)
            }
        })

    }
    function DeleteCommentPost(e) {
        var data_slug = $(e.target).attr("data-slug").split("_").at(-1);
        var url = `/social/delete-comment-post/${data_slug}/`
        console.log(url)
        $("#DeleteCommentPostModal").on("click", (ev) => {
            if ($(ev.target).attr("id") !== "deleteCommentPostBtn") return;
            ev.preventDefault();
            var _form = $("#deleteCommentPostForm")
            $.ajax({
                url: url,
                data: _form.serialize(),
                type: "post",
                dataType: "json",
                success: function (data) {
                    if (data.success) {
                        $(`#DeleteCommentPostModal`).modal('hide');
                        var comments_count = $(`.${data.post_slug}_comments_count`).text()
                        $(`.${data.post_slug}_comments_count`).text(parseInt(comments_count) - 1)
                        alertUser("Comment", "has been deleted successfully");
                        $(`.comment_instance_${data_slug}`).fadeOut("slow");
                    }
                },
                error: function (error) {
                    console.log("error", error)
                }
            })
        });
    }
    // setting the csrf token config I guess...
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    function PostLike(e) {
        $(e.target).attr("disabled", true)
        var post_slug = $(e.target).attr("data-slug").split("_")
        var slug = post_slug.at(-1)
        var liked_a = post_slug[0]
        var url = `/social/like-post/${slug}/`
        data = { "liked_a": liked_a }
        $.ajax({
            url: url,
            type: "post",
            data: data,
            dataType: "json",
            headers: { 'X-CSRFToken': csrftoken },
            mode: 'same-origin',// Do not send CSRF token to another domain.
            success: function (data) {
                var _icon = e.target.firstElementChild
                var likes_count = $(e.target).find(".likes-count").text()
                if (data.is_liked) {
                    $(e.target).find(".likes-count").text(parseInt(likes_count) - 1)
                    $(_icon).removeClass("fa").addClass("far")
                    $(_icon).parent().removeClass("is_liked")
                } else {
                    $(e.target).find(".likes-count").text(parseInt(likes_count) + 1)
                    $(_icon).removeClass("far").addClass("fa")
                    $(_icon).parent().addClass("is_liked")
                }
                $(e.target).prop("disabled", false)
            },
            error: function (error) {
                console.log("there was this error", error)
            }
        })

    }
    function cancelForgeLink(e) {
        var profile_slug = $(e.target).attr("profile-slug") ? $(e.target).attr("profile-slug") :
            (window.location.pathname).split("/").at(-2)
        data = { "profile_slug": profile_slug, "csrfmiddlewaretoken": csrftoken, }
        $.ajax({
            url: "/connection/cancel-forge-link/",
            data: data,
            type: "post",
            dataType: "json",
            success: (data) => {
                if (data.success) {
                    console.log("ok");
                    alertUser("Your request to forge a link", "has been cancelled successfully!")
                    $(e.target).attr("data-role", "ForgeNewLink")
                    $(e.target).text("Connect")
                } else {
                    alert(data.error)
                }
            },
            error: (error) => {
                console.log("there was an error");
            }
        })
    }
    function ForgeNewLink(e) {
        $(e.target).attr("disabled", true);
        $(e.target).css({ "cursor": "not-allowed" })
        var profile_slug = $(e.target).attr("profile-slug") ? $(e.target).attr("profile-slug") :
            (window.location.pathname).split("/").at(-2)
        data = { "profile_slug": profile_slug, "csrfmiddlewaretoken": csrftoken, }
        $.ajax({
            url: "/connection/sending-link-forge/",
            type: "post",
            data: data,
            dataType: "json",
            success: function (data) {
                if (data.error) {
                    alert(data.error)
                } else {
                    (e.target.id) ? $(e.target).attr("id", "CancelLinkForge") :
                        $(e.target).attr("data-role", "CancelLinkForge")
                    $(e.target).text("Cancel connection request")
                    $(e.target).prop("disabled", "false")
                    $(e.target).css({ "cursor": "pointer" })

                    alertUser(`Your Request to forge a link has been sent successfully to`, `${data.profile_owner}`)
                }

            },
            error: function (error) {
                $(e.target).prop("disabled", false)
            }
        })
    }
    function unLink(e) {
        $(e.target).attr("disabled", true)
        var request_id = $(e.target).attr("removee-id")
        data = { "removee_id": request_id, "csrfmiddlewaretoken": csrftoken, }
        $.ajax({
            url: "/connection/unlink-forge-link/",
            type: "post",
            data: data,
            dataType: "json",
            success: (data) => {
                if (data.success) {
                    var _accepted = `<p class="acceptedRequest"> You and ${data.sender} are no longer connected</p>`
                    var ul_parent = $(e.target).parent().parent()
                    ul_parent.replaceWith(_accepted);

                } else {
                    alert(data.error)
                    $(e.target).prop("disabled", false)
                }
            }
        })
    }
    function acceptLinkForge(e) {
        $(e.target).attr("disabled", true)
        $(e.target).css({ "cursor": "not-allowed" })
        var request_id = $(e.target).attr("data-request-id")
        data = { "request_id": request_id, "csrfmiddlewaretoken": csrftoken, }
        $.ajax({
            url: "/connection/accept-forge-link/",
            type: "post",
            data: data,
            dataType: "json",
            success: (data) => {
                if (data.success) {
                    //update the connection btn
                    if (($(e.target).parent().parent()).attr("id") === "requestAcc_or_dec") {
                        console.log("your are in the proifle page ")
                        $("#requestAcc_or_dec").fadeOut();
                        var con_numb = $("#all-connections").next().text()
                        console.log(con_numb);
                        $("#all-connections").next().text(parseInt(con_numb) + 1)
                    } else {
                        var _accepted = `<p class="acceptedRequest"> You and ${data.sender} are now connected</p>`
                        var ul_parent = $(e.target).parent().parent()
                        ul_parent.replaceWith(_accepted);
                    }
                    alertUser("You and ", `${data.sender} are now connected`)
                    $(e.target).prop("disabled", false)
                    $(e.target).css({ "cursor": "pointer" })
                } else {
                    alert(data.error)
                    $(e.target).prop("disabled", false)
                    $(e.target).css({ "cursor": "pointer" })
                }
            }
        })
    };
    function deleteLinkForge(e) {
        $(e.target).attr("disabled", true)
        console.log("the delete function was called")
        var request_id = $(e.target).attr("data-request-id")
        data = { "request_id": request_id, "csrfmiddlewaretoken": csrftoken, }
        $.ajax({
            url: "/connection/delete-forge-link/",
            type: "post",
            data: data,
            dataType: "json",
            success: (data) => {
                if (data.success) {
                    //update the connection btn
                    if (($(e.target).parent().parent()).attr("id") === "requestAcc_or_dec") {
                        $("#requestAcc_or_dec").fadeOut();
                    } else if ($(e.target).parent().parent().parent().attr("class") === "company_profile_info") {
                        $(e.target).parent().parent().parent().fadeOut()
                    }
                    else {
                        $(`#col_parent_${request_id}`).fadeOut();
                    }
                    alertUser("connection Request deleted", `successfully!`)
                } else {
                    alert(data.error);
                    $(e.target).prop("disabled", false)
                }
            }
        })
    }
    function timeSince(date_obj) {

        var seconds = Math.floor((new Date() - new Date(date_obj)) / 1000);
        console.log(seconds)
        var interval = seconds / 31536000;

        if (interval > 1) {
            return Math.floor(interval) + "y ago";
        }
        interval = seconds / 2592000;
        if (interval > 1) {
            return Math.floor(interval) + "m ago";
        }
        interval = seconds / 86400;
        if (interval > 1) {
            return Math.floor(interval) + "d ago";
        }
        interval = seconds / 3600;
        if (interval > 1) {
            return Math.floor(interval) + "h ago";
        }
        interval = seconds / 60;
        if (interval > 1) {
            return Math.floor(interval) + " minutes ago";
        }
        return "just now";
    }
    // this function will change the formation of the javascript object to a more human readable date
    function dateFormating(dateObj, hours = false) {
        var options1 = { "month": 'numeric', "day": 'numeric', "year": 'numeric', }
        var options2 = { "month": 'numeric', "day": 'numeric', "year": 'numeric', "hour": 'numeric', "minute": 'numeric', }
        var dateTimeFormat = Intl.DateTimeFormat('default',);

        if (dateObj === null) {
            return "None";
        } else {
            var myDate = new Date(dateObj.toString());
            if (hours) {
                var dateTimeFormat = Intl.DateTimeFormat('default', options2);
                return dateTimeFormat.format(myDate);
            } else {
                var dateTimeFormat = Intl.DateTimeFormat('default', options1);
                return dateTimeFormat.format(myDate)
            }
        }
    }
    function UpdatePostUI(_id, data_template, post_slug) {
        if (_id === "#CreatePostModal") {
            $(".posts-section").prepend(data_template)
        } else {
            $(`.posts-section [data-slug=${post_slug}]`).replaceWith(data_template);
        }
    }
    // async function srcToFile(src, fileName, mimeType) {
    //     return (fetch(src)
    //         .then(function (res) { return res.arrayBuffer(); })
    //         .then(function (buf) { return new File([buf], fileName, { type: mimeType }); })
    //     );
    // }
    async function srcToFile2(src, fileName, mimeType) {
        const res = await fetch(src)
        const arr = await res.arrayBuffer()
        return new File([arr], fileName, { type: mimeType });

    }
});