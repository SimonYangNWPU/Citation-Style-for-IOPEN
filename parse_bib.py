import os
import re
import pdb


path = os.path.join(os.path.dirname(__file__))

if __name__ == '__main__':
    file_dir = os.path.join(os.path.dirname(__file__),"20220513")
    item_list = []
    # pdb.set_trace()

    with open(os.path.join(file_dir,"mybib.bib"), "r", encoding='GBK')as f:
        res = f.read()
        # print(res)
        need_list = ["title","author","journal","volume","number","pages","year","note","date","eventtitle"]

        pattern = re.compile("[^@]+",re.DOTALL)
        # r = re.split(pattern,res)
        it = re.finditer(pattern,res)
        for match in it:
            try:
                item = match.group()
                # pdb.set_trace()

                # print(item)
                # ss_pattern = re.compile(" {1,}[a-z]+ *",re.DOTALL)
                # ss_it = re.finditer(ss_pattern,item)
                # for aaa in ss_it:

                #     bbb = aaa.group().strip()
                #     if not bbb in need_list:
                #         bbb_pt = re.compile(" {1,}{}.*".format(bbb))
                #         item=bbb_pt.sub("", item)



                arXiv_pattern = re.compile("journal *= *{arXiv preprint.*}{1}")
                arXiv_result = arXiv_pattern.search(item)
                if not arXiv_result is None:
                    tmp = arXiv_result.group()
                    # print(tmp)
                    re_arXiv = re.compile("arXiv:[0-9.]+")
                    arXiv_num = re_arXiv.search(tmp).group()

                    re_note = re.compile("note *= *{.*}{1}")

                    if not re_note.search(item) is None:
                        item=re_note.sub("note = {{{}}}".format(arXiv_num), item)
                    else:
                        re_year = re.compile("year *= *{.*}{1}")
                        note = "note = {{{}}}".format(arXiv_num)
                        year = re_year.search(item).group()

                        item=re_year.sub("{},\n  {}".format(note,year), item)

                        # print(note)


                        # print(item)

                proc_pattern = re.compile("{.+IEEE")
                proc_result = proc_pattern.search(item)

                if not proc_result is None:
                    item=proc_pattern.sub("{IEEE", item)
                    # item = item.replace("Proceedings of the ","")
                # print(item)


                name_pattern = re.compile("author *= *{.*}{1}")
                tmp_name = name_pattern.search(item).group()

                re_name = re.compile("author *= *{")
                tmp_name = re_name.sub("", tmp_name)[:-1]
                tmp_name = tmp_name.replace("author *= *{","")[:-1]
                new_author_list = []
                new_author_str = ""
                for nn in tmp_name.split(" and "):
                    p = nn.split(", ")
                    # print(p)
                    new_author_list.append("{}, {}".format(p[0], p[1].split(" ")[0]))

                # print(new_author_list)

                item=name_pattern.sub("author = {{{}}}".format(" and ".join(new_author_list)), item)
                # print(item)

                # *\([A-Z]+\) *
                sc_pattern = re.compile("booktitle.*\([A-Z 0-9]+\) *")
                sc_result = sc_pattern.search(item)
                if not sc_result is None:
                    # print(sc_result.group())
                    t_p =re.compile(" *\([A-Z 0-9]+\) *")
                    a = t_p.sub("", sc_result.group())
                    item = sc_pattern.sub(a, item)
                    # print(a)
                item_list.append("@{}".format(item))
                # print(item)
            except Exception as e:
                print(item)
                print(e)



    md_path = os.path.join(file_dir,'reference.md')
    with open(md_path, 'w', encoding='UTF-8') as temp_file:
        for index, item in enumerate(item_list):
            id_pattern = re.compile("@[a-zA-Z]+{{1}[^,]*")
            tmp_id = id_pattern.search(item).group()

            title_pattern = re.compile("title *= *{[^,]+")
            tmp_title = title_pattern.search(item).group()[7:-1]
            # print(tmp_title)
            # print("{} @[{}]".format(tmp_title, tmp_id.split("{")[1]))

            temp_file.write("\n {} [@{}] \n".format(tmp_title, tmp_id.split("{")[1]))
        temp_file.write("\n"+'-'*35 +"Ref"+'-'*35 +"\n")

    # pdb.set_trace()

    bib_path = os.path.join(file_dir,'new_bib.bib')
    with open(bib_path, 'w', encoding='UTF-8') as temp_file:
        for item in item_list:
            temp_file.write(item)

    csl_path = os.path.join(path,"iopen2022.csl")
    doc_path = os.path.join(file_dir,'citation.docx')
    # pandoc --cite --csl=iopen2022.csl  --bibliography=new_bib.bib ref.md -o demo-citation.docx -V CJKmainfont='Microsoft Yahei UI'
    command = "pandoc --cite --csl={} --bibliography={} {} -o {}".format(csl_path, bib_path, md_path, doc_path)

    os.system(command)



