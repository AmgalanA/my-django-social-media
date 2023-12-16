from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from itertools import chain
import random

from .models import Profile, Post, LikePost, FollowersCount

@login_required(login_url='signin')
def index(request):
    """
    Based on info of logged in user finds its following users, posts of these users  

    :param request: contains info  about logged in user
    :type request: {
        user: {
            username: string
        }
    }
    :return: renders index.html template with info of object: {
        user_profile: Profile of logged in user,
        posts: array of posts of subscripted profiles,
        suggestions_username_profile_list: profiles, which are not followed by current user,
    } 
    :type return: {
        user_profile: ProfileModel;
        posts: PostModel[];
        suggestions_username_profile_list: Profile[]
    }
    :raises Unauthorized
    """
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    user_following_list = []
    feed = []

    user_following = FollowersCount.objects.filter(follower=request.user.username)
    for users in user_following:
        user_following_list.append(users.user)

    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user=usernames)
        feed.append(feed_lists)

    feed_list = list(chain(*feed))

    all_users = User.objects.all()
    user_following_all = []

    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)

    new_suggestions_list = [x for x in list(all_users) if x not in list(user_following_all)]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestions_list =  [x for x in list(new_suggestions_list) if x not in list(current_user)]
    random.shuffle(final_suggestions_list)

    username_profile = []
    username_profile_list = []

    for users in final_suggestions_list:
        username_profile.append(users.id)

    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)

    suggestions_username_profile_list = list(chain(*username_profile_list))

    posts = Post.objects.all()

    return render(request, 'index.html',
                  {
                      'user_profile': user_profile,
                      'posts': feed_list,
                      'suggestions_username_profile_list': suggestions_username_profile_list[:4]
                  }
                  )

@login_required(login_url='signin')
def upload(request):
    """
    Uploads new post

    :param request: contains info  about logged in user
    :type request: {
        user: {
            username: string
        },
        FILES: FILE[],
        POST: [caption]: string[]
    }
    :returns: redirects to / path with info of object: {
        user_profile: Profile of logged in user,
        posts: array of posts of subscripted profiles,
        suggestions_username_profile_list: profiles, which are not followed by current user,
    } 
    :rtype: -
    :raises Unauthorized
    """
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()

        return redirect('/')

    else:
        return redirect('/')

@login_required(login_url='signin')
def search(request):
    """
    Implements search user by username functionality

    :param request: contains dictionary user with username inside,
                and object POST with key 'username' which is a search query
    :type request: {
        user: {
            username: string
        }
    }
    :renders: search.html template with info of object: {
        user_profile: Profile of logged in user,
        username_profile_list: list of profiles whose usernames contains search query
    } 
    :type renders: {
        user_profile: ProfileModel;
        username_profile_list: ProfileModel[];
    }
    :raises BadRequest or Unauthorized
    """
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)

        username_profile = []
        username_profile_list = []

        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)

        username_profile_list = list(chain(*username_profile_list))

    return render(request, 'search.html',
                  {
                      'user_profile': user_profile,
                      'username_profile_list': username_profile_list,
                  }
                  )

@login_required(login_url='signin')
def like_post(request):
    """
    Implements like post functionality. Increments count of likes if user has not liked the post,
    and decrements if user has.

    :param request: contains info  about logged in user
            ans GET param key with property 'post_id'
    :type request: {
        user: {
            username: string,
            GET: {
                post_id: string
            }
        }
    }
    :redirects: to '/' with no properties
    :raises BadRequest or Unauthorized
    """
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes = post.no_of_likes + 1
        post.save()
    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes - 1
        post.save()
    return redirect('/')

@login_required(login_url='signin')
def delete_post(request):
    """
    Deletes post

    :param request: contains id of post with key 'post_id'
    :type request: {
        POST: {
            post_id: string
        }
    }
    :redirects: '/'
    :raises BadRequest or Unauthorized
    """
    post_id = request.POST.get('post_id')

    Post.objects.filter(id=post_id).delete()

    return redirect('/')

@login_required(login_url='signin')
def profile(request, pk):
    """
    Returns profile with specific username of logged in user,
    returns all posts of that user,
    and who is following him and who is followed by him

    :param request: contains user object with username;
            pk: name of logged in user
    :type request: {
        user: {
            username: string
        },
        pk: string
    }
    :renders: profile.html template with info of object: {
        user_object: current user;
        user_profile: profile with username;
        user_posts: posts of user;
        user_post_length: length of posts;
        button_text: text for subscribe button;
        user_followers: amount of followers;
        user_following: amount of following user;
    } 
    :type renders: {
        user_object: UserModel;
        user_profile: ProfileModel;
        user_posts: PostModel[];
        user_post_length: number;
        button_text: string;
        user_followers: number;
        user_following: number;
    }
    :raises BadRequest or Unauthorized
    """
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_post_length = len(user_posts)

    follower = request.user.username
    user = pk

    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'

    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))
    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
    }

    return render(request, 'profile.html', context)

@login_required(login_url='signin')
def follow(request):
    """
    Implements follow functionality

    :param request: contains info  about logged in user,
            and user he or she wants to follow
    :type request: {
        POST: {
            user: string;
            follower: string;
        }
    }
    :redirects: 
        1) to profile + username page if request.method == "POST"
        2) to / if request.method == "GET"
    :raises BadRequest or Unauthorized 
    """
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
        return redirect('/profile/' + user)

    else:
        return redirect('/')

@login_required(login_url='signin')
def settings(request):
    """
    If user wants to get settings page, it redirects to /settings page with info about logged in profile
    If user wants to post settings page, it gets all info from submitted form and changes info in profile model 

    :param request: contains username of logged in user
    :type request: {
        user: string
    }
    :renders: settings.html template with info of object: {
        user_profile: Profile of logged in user,
    } 
    :type renders: {
        user_profile: ProfileModel;
    }
    :raises BadRequest or Unauthorized
    """
    user_profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        requestImage = request.FILES.get('image')
        if requestImage == None:
            image = user_profile.profileimg
        elif requestImage != None:
            image = requestImage

        bio = request.POST['bio']
        location = request.POST['location']
        user_profile.profileimg = image
        user_profile.bio = bio
        user_profile.location = location

        user_profile.save()

        return redirect('settings')

    return render(request, 'setting.html', {
        'user_profile': user_profile,
    })

def signup(request):
    """
    Implements sign up functionality

    :param request: {
        POST: {
            username: name from form data;
            email: email from form data;
            password: password from form data;
            password2: second password from form data;
        }
    }
    :type request: {
        POST: {
            username: name from form data;
            email: email from form data;
            password: password from form data;
            password2: second password from form data;
        }
    }
    :renders: signup.html template
    :raises BadRequest with messages Email Already Taken, Username Already Taken, Passwords not matching or Unauthorized 
    """
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if (password == password2):
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Already Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Already Taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                # log user in and redirect to settings page
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                # create a Profile object for the new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')

        else:
            messages.info(request, 'Passwords Not Matching')
            return redirect('/signup')

    else:
        return render(request, 'signup.html')

def signin(request):
    """
    :param request: contains info  about username and password, user has sent through form submition
    :type request: {
        POST: {
            username: name data,
            password: password data
        }
    }
    :renders: signin.html template  
    :raises BadRequest or Unauthorized
    """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if (user is not None):
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('signin')
    else:
        return render(request, 'signin.html')

@login_required(login_url='signin')
def logout(request):
    """
    :param request: contains info  about logged in user
    :type request: {
        user: {
            username: string
        }
    }
    :redirects: /signin
    :raises BadRequest or Unauthorized
    """
    auth.logout(request)
    return redirect('/signin')