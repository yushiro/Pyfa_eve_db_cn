# coding:utf-8

import sqlite3

list_market_group_parents = [(11, "Ammunition & Charges"),
                (157, "Drones"),
                (24, "Implants & Boosters"),
                (1111, "Rigs"),
                (9, "Ship Equipment"),
                (1112, "Subsystems")]


def groups_nochild_extractor(cursor, list_groups, tuple_parent):
    sql = ("select marketGroupID,marketGroupName "
           "from invmarketgroups "
           "where parentGroupID = {0} "
           "order by marketGroupName").format(tuple_parent[0])
    cursor.execute(sql)
    list_tuple_children = cursor.fetchall()
    if len(list_tuple_children) > 0:
        for each_tuple_children in list_tuple_children:
            groups_nochild_extractor(cursor, list_groups, (each_tuple_children[
                                     0], "{0}-{1}".format(tuple_parent[1], each_tuple_children[1])))
    else:
        list_groups.append(tuple_parent)


def items_dict_load(items_file_path):
    file_to_read = open(items_file_path, 'r')
    lines = file_to_read.readlines()
    file_to_read.close()
    dict_items = {}
    for each_line in lines:
        each_pair = each_line.strip('\n\r').split(',')
        dict_items[each_pair[0].replace("''", "'")] = each_pair[1]
    return dict_items


def items_execute(cursor, exec_file_path, list_groups, dict_items):

    file_tmp = open(exec_file_path, 'w')

    for each_group in list_groups:
        sql = ("select typeName from invtypes "
               "left join invmetatypes "
               "on invmetatypes.typeID = invtypes.typeID "
               "where marketGroupID = {0} "
               "order by invmetatypes.metaGroupID,typeName").format(each_group[0])
        cursor.execute(sql)
        list_items_each_group = cursor.fetchall()
        if len(list_items_each_group) > 0:
            print >> file_tmp, "**********{0}**********".format(each_group[1])
            for each_item in list_items_each_group:
                if dict_items.has_key(each_item[0]):
                    print >> file_tmp, "{0},{1}".format(
                        each_item[0].encode('utf-8').replace("'", "''"), dict_items[each_item[0]])
                else:
                    print >> file_tmp, "{0},{1}".format(
                        each_item[0].encode('utf-8').replace("'", "''"), "")

    file_tmp.flush()
    file_tmp.close()


def main():

    # 连接数据库
    conn = sqlite3.connect('eve.db')
    cursor = conn.cursor()

    # 获取没有下级菜单的市场组list
    list_groups = []
    for parent in list_market_group_parents:
        groups_nochild_extractor(cursor, list_groups, parent)

    # 加载汉化物品字典
    dict_items = items_dict_load("locate/po/ItemsNonFiltered.tmp")

    # 分组输出items的name和namecn
    items_execute(cursor, 'locate/po/ItemsGroupby.tmp',
                  list_groups, dict_items)

    # 关闭数据库
    cursor.close()
    conn.commit()
    conn.close()

if __name__ == '__main__':
    main()
