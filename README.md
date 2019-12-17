# averrage_face

how to run: 
```shell
python3 pj.py
```

and you can modify the config in config.py：

```python
Config = {
    'img_dir' : './testset/test5/pic', #The path of your images' folder
    'w' : 500,	#The width of your final image
    'h' : 600,	#The height of your final image
    'background': '373.jpg',	#Choose your background image.The final average image would based on the hair, shirt, background that the original image you choose. If the file of background dose not exsit, the programe would use the first one read as the background.
}
```


## main featrue of this project

basically most of the average projects generate the final image like those below: 
![image](https://github.com/Jeret-Ljt/average_face/blob/master/readme_materials/1.PNG)
![image](https://github.com/Jeret-Ljt/average_face/blob/master/readme_materials/5.PNG)

but our project's pictures have clear backgrounds which are chosen in the config.py 
and our final images are like those:
![image](https://github.com/Jeret-Ljt/average_face/blob/master/testset/test4/pic_result/result.jpg)
![image](https://github.com/Jeret-Ljt/average_face/blob/master/testset/test1/test_result/mix.jpg)

the first two images in the left are the original images, and the last is the generated one.
