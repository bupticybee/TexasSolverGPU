import tkinter as tk
from tkinter import Tk
import tkinter.messagebox
import tkinter.ttk as ttk
import json
import numpy as np
from tkinter import filedialog as fd
import argparse

filetypes = (
    ('json files', '*.json'),
    ('All files', '*.*')
)

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--file')
parser.add_argument('--title',default="")
args = parser.parse_args()

root = tk.Tk()
root.geometry("1440x720")
root.minsize(1620, 720)
root.maxsize(1620, 720)
root.title("Strategy Viewer" + args.title)

if args.file:
    filename = args.file
else:
    filename = fd.askopenfilename(
        title='Open a file',
        initialdir='./',
        filetypes=filetypes)

with open(filename, 'r') as fhdl:
    dumped_strategy = json.load(fhdl)

tree = ttk.Treeview(root, height=20)
tree.heading('#0', text='GameTree', anchor=tk.W)
tree.column("#0", width=360, minwidth=360)

iid = 0
tree.insert('', tk.END, text='Round start', iid=0, open=False)
info_dic = {0: dumped_strategy}
cards = "AKQJT98765432"

display_type = "strategy_with_range"


def re_insert_treenode(json_node, parent_iid):
    global iid
    global info_dic
    if not json_node:
        return
    if "childrens" in json_node and json_node["childrens"]:
        children_idx = 0
        node_player = json_node["player"]
        if json_node["type"] == "action":
            for one_children, valid_actions in zip(json_node["childrens"], json_node["valid_actions"]):
                iid += 1
                tree.insert('', tk.END, text=f"P{node_player} " + valid_actions, iid=iid, open=False)
                tree.move(iid, parent_iid, children_idx)
                info_dic[iid] = one_children
                children_idx += 1
                re_insert_treenode(one_children, parent_iid=iid)
        elif json_node["type"] == "chance":
            for one_card in json_node["childrens"]:
                one_children = json_node["childrens"][one_card]
                iid += 1
                tree.insert('', tk.END, text=f"Chance {one_card}", iid=iid, open=False)
                tree.move(iid, parent_iid, children_idx)
                info_dic[iid] = one_children
                children_idx += 1
                re_insert_treenode(one_children, parent_iid=iid)


def arrange_strategy(strategy):
    ret_strategy = {}
    ret_strategy_prob_sum = {}
    ret_strategy_prob_sum_normed = {}
    spec_strategy = {}

    spec_range = {}

    global overall_strategy
    overall_strategy = None
    for one_card_string, one_reach_prob, one_strategy in zip(strategy["card_strings"], strategy["reach_probs"],
                                                             strategy["strategy_probs"]):
        if overall_strategy is None:
            overall_strategy = np.asarray(one_strategy) * one_reach_prob
        else:
            overall_strategy += np.asarray(one_strategy) * one_reach_prob
        if one_card_string[0] == one_card_string[2]:
            info_str = f"{one_card_string[0]}{one_card_string[2]}"
        elif one_card_string[1] == one_card_string[3]:
            idx1 = cards.index(one_card_string[0])
            idx2 = cards.index(one_card_string[2])
            if idx1 < idx2:
                info_str = f"{one_card_string[0]}{one_card_string[2]}s"
            else:
                info_str = f"{one_card_string[2]}{one_card_string[0]}s"
        else:
            idx1 = cards.index(one_card_string[0])
            idx2 = cards.index(one_card_string[2])
            if idx1 < idx2:
                info_str = f"{one_card_string[0]}{one_card_string[2]}o"
            else:
                info_str = f"{one_card_string[2]}{one_card_string[0]}o"

        ret_strategy.setdefault(info_str, [])
        ret_strategy_prob_sum.setdefault(info_str, 0)
        ret_strategy_prob_sum_normed.setdefault(info_str, 0)
        ret_strategy[info_str].append(np.asarray(one_strategy) * one_reach_prob)
        ret_strategy_prob_sum[info_str] += one_reach_prob

        if "o" == info_str[-1]:
            ret_strategy_prob_sum_normed[info_str] += one_reach_prob / 12.0
        elif "s" == info_str[-1]:
            ret_strategy_prob_sum_normed[info_str] += one_reach_prob / 4.0
        else:
            ret_strategy_prob_sum_normed[info_str] += one_reach_prob / 6.0

        spec_strategy.setdefault(info_str, [])
        spec_strategy[info_str].append({
            "cards": one_card_string,
            "strategy": one_strategy,
        })

        spec_range.setdefault(info_str, [])
        spec_range[info_str].append({
            "cards": one_card_string,
            "range": one_reach_prob,
        })

    for k in ret_strategy:
        ret_strategy[k] = np.sum(
            np.asarray(ret_strategy[k]), axis=0) / ret_strategy_prob_sum[k]
        #assert (np.isclose(np.sum(ret_strategy[k]), 1))
    overall_strategy = overall_strategy / np.sum(overall_strategy)
    return ret_strategy, spec_strategy, ret_strategy_prob_sum_normed, spec_range


n = 13
lngt = 720 // n  # this is the dimension of the squares that I want
detail_strategy_info = []
detail_range_info = []
valid_actions = []
overall_strategy = []
clicked_info = None

last_click_iid = None


def on_click_treeview(event):
    global last_click_iid
    iid = tree.identify('item', event.x, event.y)
    if not iid:
        return
    last_click_iid = iid
    on_click_iid()


def on_click_iid():
    global detail_strategy_info
    global detail_range_info
    global valid_actions
    global clicked_info
    iid = last_click_iid
    if iid is None:
        return

    clicked_info = info_dic[int(iid)]
    if not clicked_info:
        return
    if "strategy" in clicked_info:
        strategy = clicked_info["strategy"]
        strategy, spec_strategy, range_prob, spec_range = arrange_strategy(strategy)

    max_val = np.max(list(range_prob.values()))

    can.delete("all")
    valid_actions = clicked_info["valid_actions"]

    print(valid_actions)

    detail_strategy_info = []
    detail_range_info = []


    for i in range(n):
        tmp_detail_strategy_info = []
        tmp_detail_range_info = []

        y = i * lngt
        for j in range(n):
            if i > j:
                info = f"{cards[j]}{cards[i]}o"
            elif i < j:
                info = f"{cards[i]}{cards[j]}s"
            else:
                info = f"{cards[i]}{cards[j]}"

            x = j * lngt

            if display_type == "strategy":
                strategy_probs = strategy.get(info, None)
                one_spec_strategy = spec_strategy.get(info, None)

                tmp_detail_strategy_info.append(one_spec_strategy)
                if strategy_probs is None or len(strategy_probs) == 0:
                    can.create_rectangle(x, y, x + lngt, y + lngt, fill="grey", outline="")
                    can.create_text(x + 20, y + 10, text=info, fill="black", font=('Helvetica 15 bold'))
                    can.create_rectangle(x, y, x + lngt, y + lngt, fill="")
                    continue

                can.create_rectangle(x, y, x + lngt, y + lngt, fill="blue", outline="")

                fold_range = 0
                if "Fold" == valid_actions[0]:
                    fold_range = strategy_probs[0]
                    actions = valid_actions[1:]
                    probs = strategy_probs[1:] / (np.sum(strategy_probs[1:]) + 1e-20)
                else:
                    actions = valid_actions[:]
                    probs = strategy_probs[:] / np.sum(strategy_probs[:] + 1e-20)

                assert (np.isclose(np.sum(probs), 1) or np.isclose(np.sum(probs), 0))

                offset_fold = lngt * fold_range

                pixels = [0]
                for one_pidx in range(len(probs)):
                    pixels.append(int(np.sum(probs[:one_pidx + 1]) * lngt))
                pixels[-1] = lngt

                color_list = ["deeppink", "red", "red2", "red3", "red4"]
                raise_ind = 0
                for action_idx, one_action, one_prob in zip(list(range(len(actions))), actions, probs):
                    if one_action == "Call":
                        color = "green"
                    elif one_action == "Check":
                        color = "lightgreen"
                    elif one_action == "All-In":
                        color = "darkred"
                    else:
                        assert ("Raise" in one_action)
                        color = color_list[raise_ind]
                        raise_ind += 1
                    can.create_rectangle(x + pixels[action_idx], y + offset_fold, x + pixels[action_idx + 1], y + lngt,
                                         fill=color, outline="")

                can.create_text(x + 20, y + 10, text=info, fill="black", font=('Helvetica 15 bold'))

                for action_idx, one_action, one_prob in zip(list(range(len(valid_actions))), valid_actions,
                                                            strategy_probs):
                    can.create_text(x + 30, y + 20 + 6 * action_idx, text=f"{one_action} {one_prob * 100:.0f}%",
                                    fill="black", font=('Helvetica 6 bold'))
                can.create_rectangle(x, y, x + lngt, y + lngt, fill="")
            elif display_type == "range":
                reach_probs = range_prob.get(info, None)
                one_spec_reach = spec_range.get(info, None)

                tmp_detail_range_info.append(one_spec_reach)
                if reach_probs is None:
                    can.create_rectangle(x, y, x + lngt, y + lngt, fill="grey", outline="")
                    can.create_text(x + 20, y + 10, text=info, fill="black", font=('Helvetica 15 bold'))
                    can.create_rectangle(x, y, x + lngt, y + lngt, fill="")
                    continue

                normed_reach = reach_probs / max_val
                offset_reach = int((1 - normed_reach) * lngt)
                can.create_rectangle(x, y + offset_reach, x + lngt, y + lngt, fill="yellow", outline="")
                can.create_text(x + 20, y + 10, text=info, fill="black", font=('Helvetica 15 bold'))
                can.create_text(x + 40, y + 20, text=f"{reach_probs:.5e}", fill="black", font=('Helvetica 5 bold'))
                can.create_rectangle(x, y, x + lngt, y + lngt, fill="")
            elif display_type == "strategy_with_range":
                # range
                reach_probs = range_prob.get(info, None)
                one_spec_reach = spec_range.get(info, None)
                tmp_detail_range_info.append(one_spec_reach)

                strategy_probs = strategy.get(info, None)
                one_spec_strategy = spec_strategy.get(info, None)
                tmp_detail_strategy_info.append(one_spec_strategy)
                if reach_probs is None:
                    can.create_rectangle(x, y, x + lngt, y + lngt, fill="grey", outline="")
                    can.create_text(x + 20, y + 10, text=info, fill="black", font=('Helvetica 15 bold'))
                    can.create_rectangle(x, y, x + lngt, y + lngt, fill="")
                    continue

                normed_reach = reach_probs / max_val
                offset_reach = (1 - normed_reach)

                # strategy
                if strategy_probs is None:
                    can.create_rectangle(x, y, x + lngt, y + lngt, fill="grey", outline="")
                    can.create_text(x + 20, y + 10, text=info, fill="black", font=('Helvetica 15 bold'))
                    can.create_rectangle(x, y, x + lngt, y + lngt, fill="")
                    continue

                can.create_rectangle(x, y, x + lngt, y + lngt, fill="grey", outline="")

                fold_range = offset_reach
                actions = valid_actions[:]
                probs = strategy_probs[:] / np.sum(strategy_probs[:] + 1e-20)

                assert (np.isclose(np.sum(probs), 1) or np.isclose(np.sum(probs), 0))

                offset_fold = lngt * fold_range

                pixels = [0]
                for one_pidx in range(len(probs)):
                    pixels.append(int(np.sum(probs[:one_pidx + 1]) * lngt))
                pixels[-1] = lngt

                color_list = ["deeppink", "red", "red2", "red3", "red4"]
                raise_ind = 0
                for action_idx, one_action, one_prob in zip(list(range(len(actions))), actions, probs):
                    if one_action == "Fold":
                        color = "blue"
                    elif one_action == "Call":
                        color = "green"
                    elif one_action == "Check":
                        color = "lightgreen"
                    elif one_action == "All-In":
                        color = "darkred"
                    else:
                        assert ("Raise" in one_action)
                        color = color_list[raise_ind]
                        raise_ind += 1
                    can.create_rectangle(x + pixels[action_idx], y + offset_fold, x + pixels[action_idx + 1], y + lngt,
                                         fill=color, outline="")

                can.create_text(x + 20, y + 10, text=info, fill="black", font=('Helvetica 15 bold'))

                for action_idx, one_action, one_prob in zip(list(range(len(valid_actions))), valid_actions,
                                                            strategy_probs):
                    can.create_text(x + 30, y + 20 + 6 * action_idx, text=f"{one_action} {one_prob * 100:.0f}%",
                                    fill="black", font=('Helvetica 6 bold'))
                can.create_rectangle(x, y, x + lngt, y + lngt, fill="")
            else:
                raise


        detail_strategy_info.append(tmp_detail_strategy_info)
        detail_range_info.append(tmp_detail_range_info)

    can_detail.delete("all")

    ind_y = 500
    can_detail.create_text(200, ind_y, text="Overall Strategy:", fill="black", font=('Helvetica 20 bold'))
    for one_key,one_val in zip(valid_actions,overall_strategy):
        ind_y += 20
        can_detail.create_text(200, ind_y, text=one_key + " : " + str(round(one_val * 100,1)), fill="black", font=('Helvetica 20 bold'))
    print("ending")


def on_click_item(event):
    xind = event.x // lngt
    yind = event.y // lngt
    print(xind, yind)

    can_detail.delete("all")

    can_detail.create_text(200, 40, text="table: " + clicked_info["table_cards"], fill="black", font=('Helvetica 20 bold'))
    can_detail.create_text(200, 60, text="player: " + str(clicked_info["player"]), fill="black", font=('Helvetica 20 bold'))
    can_detail.create_text(200, 80, text="node type: " + clicked_info["type"], fill="black", font=('Helvetica 20 bold'))
    can_detail.create_text(200, 100, text="betting round: " + ["preflop","flop","turn","river"][clicked_info["betting round"]], fill="black", font=('Helvetica 20 bold'))
    can_detail.create_text(200, 120, text="node type: " + str(clicked_info["pot"]), fill="black", font=('Helvetica 20 bold'))

    ind_y = 500
    can_detail.create_text(200, ind_y, text="Overall Strategy:", fill="black", font=('Helvetica 20 bold'))
    for one_key,one_val in zip(valid_actions,overall_strategy):
        ind_y += 20
        can_detail.create_text(200, ind_y, text=one_key + " : " + str(round(one_val * 100,1)), fill="black", font=('Helvetica 20 bold'))

    if display_type == "strategy" or display_type == "strategy_with_range":

        one_detail_strag = detail_strategy_info[yind][xind]


        if one_detail_strag is None:
            return

        if not one_detail_strag:
            return

        lngt_det = 540 / 4

        x = 0
        y = lngt_det


        for one_specific in one_detail_strag:
            one_card_str = one_specific["cards"]
            strategy_probs = one_specific["strategy"]
            print(one_card_str,strategy_probs)

            can_detail.create_rectangle(x, y, x + lngt_det, y + lngt_det, fill="blue", outline="")

            fold_range = 0
            if "Fold" == valid_actions[0]:
                fold_range = strategy_probs[0]
                actions = valid_actions[1:]
                probs = strategy_probs[1:] / (np.sum(strategy_probs[1:]) + 1e-20)
            else:
                actions = valid_actions[:]
                probs = strategy_probs[:] / (np.sum(strategy_probs[:]) + 1e-20)

            assert (np.isclose(np.sum(probs), 1) or np.isclose(np.sum(probs), 0))

            offset_fold = lngt_det * fold_range

            pixels = [0]
            for one_pidx in range(len(probs)):
                pixels.append(int(np.sum(probs[:one_pidx + 1]) * lngt_det))
            pixels[-1] = lngt_det

            color_list = ["deeppink", "red", "red2", "red3", "red4"]
            raise_ind = 0
            for action_idx, one_action, one_prob in zip(list(range(len(actions))), actions, probs):
                if one_action == "Call":
                    color = "green"
                elif one_action == "Check":
                    color = "lightgreen"
                elif one_action == "All-In":
                    color = "darkred"
                else:
                    assert ("Raise" in one_action)
                    color = color_list[raise_ind]
                    raise_ind += 1
                can_detail.create_rectangle(x + pixels[action_idx], y + offset_fold, x + pixels[action_idx + 1],
                                            y + lngt_det, fill=color,
                                            outline="")

            can_detail.create_text(x + 50, y + 20, text=one_card_str, fill="black", font=('Helvetica 20 bold'))

            for action_idx, one_action, one_prob in zip(list(range(len(valid_actions))), valid_actions, strategy_probs):
                can_detail.create_text(x + 80, y + 70 + 12 * action_idx, text=f"{one_action} {one_prob * 100:.0f}%",
                                       fill="black",
                                       font=('Helvetica 12 bold'))
            can_detail.create_rectangle(x, y, x + lngt_det, y + lngt_det, fill="")
            x += lngt_det
            if x >= lngt_det * 4:
                x = 0
                y += lngt_det
    elif display_type == "range":
        one_detail_range = detail_range_info[yind][xind]


        if one_detail_range is None:
            return

        if not one_detail_range:
            return

        lngt_det = 540 / 4

        x = 0
        y = lngt_det

        for one_specific in one_detail_range:
            one_card_str = one_specific["cards"]
            range_probs = one_specific["range"]
            print(one_card_str,range_probs)

            can_detail.create_text(x + 80, y + 70 + 5, text=f"{range_probs:.5e}",
                                   fill="black",
                                   font=('Helvetica 10 bold'))
            can_detail.create_text(x + 50, y + 20, text=one_card_str, fill="black", font=('Helvetica 20 bold'))
            can_detail.create_rectangle(x, y, x + lngt_det, y + lngt_det, fill="")

            x += lngt_det
            if x >= lngt_det * 4:
                x = 0
                y += lngt_det
    else:
        raise


re_insert_treenode(dumped_strategy, 0)

# place the Treeview widget on the root window
tree.grid(row=0, column=0, sticky=tk.NSEW)

tree.bind('<ButtonRelease-1>', on_click_treeview)

can = tk.Canvas(root, width=720, height=720, bg="lightblue")

can.grid(row=0, column=1, sticky=tk.NSEW)

can.bind('<ButtonRelease-1>', on_click_item)

can_detail = tk.Canvas(root, width=540, height=720, bg="white")

can_detail.grid(row=0, column=2, sticky=tk.NSEW)

# Creating a Button
value_inside = tk.StringVar(root)
# Set the default value of the variable
value_inside.set(display_type)


def on_click_switch(selection):
    global display_type
    display_type = selection
    on_click_iid()


btn = tk.OptionMenu(root, value_inside, "strategy_with_range", "strategy", "range", command=on_click_switch)

# Set the position of button to coordinate (100, 20)
btn.place(x=250, y=0)

def copy_range_str():
    r = Tk()
    r.withdraw()
    r.clipboard_clear()

    range_str = ""
    max_v = 0
    if detail_range_info:
        for one_line in detail_range_info:
            for one_col in one_line:
                if one_col is not None:
                    for one_card in one_col:
                        card_prob = one_card["range"]
                        max_v = max(card_prob,max_v)
        for one_line in detail_range_info:
            for one_col in one_line:
                if one_col is not None:
                    for one_card in one_col:
                        card_str = one_card["cards"]
                        card_str = card_str[2:] + card_str[:2]
                        card_prob = one_card["range"]
                        range_str += f"{card_str}:{card_prob/max_v:.5f},"
    if range_str:
        range_str = range_str[:-1]
        """
        range str example:
        Ah6h:0.02376,Ah4h:0.08209,Ah3h:0.14981,Ah2h:0.16706,AcKh:0.00003,AdKh:0.00003,AhKc:0.00003,AdKc:0.00003,AhKd:0.00003,AcKd:0.00003,KhQh:0.00087,KhJh:0.00146,KcJc:0.00469,KdJd:0.00469,KhTh:0.01090,KcTc:0.01546,KdTd:0.01546,Kh9h:0.19863,Kc9c:0.01627,Kd9d:0.01627,Kh8h:0.02259,Kh7h:0.31624,Kc7c:0.00962,Kd7d:0.00962,Kh6h:0.45550,Kc6c:0.08481,Kd6d:0.08481,Kh4h:0.05747,Kc4c:0.14948,Kd4d:0.14948,Kh3h:0.01596,Kh2h:0.41555,KhQs:0.00789,KcQs:0.00143,KdQs:0.00143,KcQh:0.03707,KdQh:0.03707,KhQc:0.07701,KhQd:0.07701,QhQs:0.00011,QcQs:0.00011,QdQs:0.00011,QcQh:0.00011,QdQh:0.00011,QdQc:0.00011,QhJh:0.13782,QcJc:0.00452,QdJd:0.00452,QhTh:0.12517,QcTc:0.00563,QdTd:0.00563,Qh9h:0.87125,Qc9c:0.87698,Qd9d:0.87698,Qs8s:0.00964,Qh8h:1.00000,Qc8c:0.99204,Qd8d:0.99204,Qs7s:0.00988,Qh7h:0.98296,Qc7c:0.97977,Qd7d:0.97977,Qh6h:0.53206,Qc6c:0.54044,Qd6d:0.54044,Qc5c:0.31286,Qd5d:0.31286,Qh4h:0.88461,Qc4c:0.89578,Qd4d:0.89578,Qs3s:0.00178,Qh3h:0.75145,Qc3c:0.81195,Qd3d:0.81195,Qh2h:0.60145,Qc2c:0.81377,Qd2d:0.81377,KcJs:0.00253,KdJs:0.00253,KcJh:0.14538,KdJh:0.14538,KhJc:0.02775,KhJd:0.02775,QhJs:0.00472,QcJs:0.01829,QdJs:0.01829,QsJh:0.02449,QcJh:0.18941,QdJh:0.18941,QsJc:0.00546,QhJc:0.33008,QdJc:0.00007,QsJd:0.00546,QhJd:0.33008,QcJd:0.00007,JhTh:0.07206,JcTc:0.04186,JdTd:0.04186,Js9s:0.00410,Jh9h:0.96888,Jc9c:0.97686,Jd9d:0.97686,Jh8h:0.87066,Jc8c:0.88213,Jd8d:0.88213,Js7s:0.00397,Jh7h:0.73164,Jc7c:0.75702,Jd7d:0.75702,Jh6h:0.86500,Jc6c:0.87644,Jd6d:0.87644,Jc5c:0.61717,Jd5d:0.61717,Js4s:0.01070,Jh4h:0.82061,Jc4c:0.84900,Jd4d:0.84900,Jh3h:0.76834,Jc3c:0.79721,Jd3d:0.79721,Jh2h:0.48672,Jc2c:0.85572,Jd2d:0.85572,KhTs:0.00290,KcTs:0.00773,KdTs:0.00773,KcTh:0.27590,KdTh:0.27590,KhTc:0.11498,KdTc:0.00234,KhTd:0.11498,KcTd:0.00234,QhTs:0.00532,QcTs:0.03172,QdTs:0.03172,QsTh:0.02365,QcTh:0.23406,QdTh:0.23406,QsTc:0.00550,QhTc:0.20624,QdTc:0.02671,QsTd:0.00550,QhTd:0.20624,QcTd:0.02671,JhTs:0.02211,JcTs:0.02759,JdTs:0.02759,JsTh:0.02016,JcTh:0.66752,JdTh:0.66752,JsTc:0.03728,JhTc:0.91987,JdTc:0.02439,JsTd:0.03728,JhTd:0.91987,JcTd:0.02439,ThTs:0.00005,TcTs:0.00005,TdTs:0.00005,TcTh:0.00005,TdTh:0.00005,TdTc:0.00005,Th9h:0.53850,Tc9c:0.54043,Td9d:0.54043,Th8h:0.78502,Tc8c:0.79485,Td8d:0.79485,Ts7s:0.00486,Th7h:0.71748,Tc7c:0.72508,Td7d:0.72508,Ts6s:0.01441,Th6h:0.77964,Tc6c:0.85954,Td6d:0.85954,Tc5c:0.64230,Td5d:0.64230,Ts4s:0.00925,Th4h:0.81775,Tc4c:0.95800,Td4d:0.95800,Th3h:0.56908,Tc3c:0.81972,Td3d:0.81972,Ts2s:0.00423,Th2h:0.91239,Tc2c:0.81955,Td2d:0.81955,Kh9s:0.03358,Kc9s:0.00761,Kd9s:0.00761,Kc9h:0.44090,Kd9h:0.44090,Kh9c:0.03412,Kd9c:0.01357,Kh9d:0.03412,Kc9d:0.01357,Qh9s:0.65916,Qc9s:0.69324,Qd9s:0.69324,Qs9h:0.49252,Qc9h:0.70401,Qd9h:0.70401,Qs9c:0.69575,Qh9c:0.69863,Qd9c:0.70209,Qs9d:0.69575,Qh9d:0.69863,Qc9d:0.70209,Jh9s:0.71803,Jc9s:0.95607,Jd9s:0.95607,Js9h:0.96395,Jc9h:0.96395,Jd9h:0.96395,Js9c:0.94193,Jh9c:0.86469,Jd9c:0.96395,Js9d:0.94193,Jh9d:0.86469,Jc9d:0.96395,Th9s:0.18524,Tc9s:0.53750,Td9s:0.53750,Ts9h:0.19213,Tc9h:0.52899,Td9h:0.52899,Ts9c:0.40782,Th9c:0.53750,Td9c:0.53750,Ts9d:0.40782,Th9d:0.53750,Tc9d:0.53750,9h9s:0.00006,9c9s:0.00006,9d9s:0.00006,9c9h:0.00006,9d9h:0.00006,9d9c:0.00006,9s8s:0.00258,9h8h:0.22559,9c8c:0.22671,9d8d:0.22671,9s7s:0.00203,9h7h:0.96757,9c7c:0.96757,9d7d:0.96757,9s6s:0.00230,9h6h:0.48611,9c6c:0.49833,9d6d:0.49833,9c5c:0.32622,9d5d:0.32622,9s4s:0.00895,9h4h:0.69592,9c4c:0.81429,9d4d:0.81429,9s3s:0.02416,9h3h:0.64028,9c3c:0.89115,9d3d:0.89115,9s2s:0.00670,9h2h:0.46086,9c2c:0.85156,9d2d:0.85156,Ah8c:0.06841,Ah8d:0.06841,Kh8s:0.03847,Kc8s:0.01074,Kd8s:0.01074,Kc8h:0.23409,Kd8h:0.23409,Qh8s:0.60492,Qc8s:0.77572,Qd8s:0.77572,Qs8h:0.79608,Qc8h:0.79608,Qd8h:0.79608,Qs8c:0.77723,Qh8c:0.79608,Qd8c:0.78682,Qs8d:0.77723,Qh8d:0.79608,Qc8d:0.78682,Jh8s:0.91179,Jc8s:0.64539,Jd8s:0.64539,Js8h:0.68364,Jc8h:0.90516,Jd8h:0.90516,Js8c:0.91083,Jh8c:0.90382,Jd8c:0.90977,Js8d:0.91083,Jh8d:0.90382,Jc8d:0.90977,Th8s:0.29126,Tc8s:0.84724,Td8s:0.84724,Ts8h:0.62562,Tc8h:0.36244,Td8h:0.36244,Ts8c:0.85741,Th8c:0.79205,Td8c:0.82775,Ts8d:0.85741,Th8d:0.79205,Tc8d:0.82775,9h8s:0.38833,9c8s:0.74937,9d8s:0.74937,9s8h:0.67378,9c8h:0.67923,9d8h:0.67923,9s8c:0.73949,9h8c:0.22804,9d8c:0.84163,9s8d:0.73949,9h8d:0.22804,9c8d:0.84163,8h8s:0.01198,8c8s:0.01914,8d8s:0.01914,8c8h:0.57001,8d8h:0.57001,8d8c:0.61153,8s7s:0.00584,8h7h:0.95191,8c7c:0.99508,8d7d:0.99508,8s6s:0.00480,8h6h:0.66536,8c6c:0.67340,8d6d:0.67340,8c5c:0.19262,8d5d:0.19262,8h4h:0.21118,8c4c:0.24559,8d4d:0.24559,8h3h:0.24530,8c3c:0.26156,8d3d:0.26156,8s2s:0.00501,8h2h:0.01513,8c2c:0.57771,8d2d:0.57771,Kh7s:0.01141,Kc7s:0.01322,Kd7s:0.01322,Kc7h:0.88135,Kd7h:0.88135,Kh7c:0.46252,Kd7c:0.00514,Kh7d:0.46252,Kc7d:0.00514,Qh7s:0.00001,Qc7s:0.00001,Qd7s:0.00001,Qs7h:0.00001,Qc7h:0.00001,Qd7h:0.00001,Qs7c:0.00001,Qh7c:0.00001,Qd7c:0.00001,Qs7d:0.00001,Qh7d:0.00001,Qc7d:0.00001,Th7s:0.01080,Tc7s:0.01081,Td7s:0.01081,Ts7h:0.00020,Tc7h:0.00768,Td7h:0.00768,Ts7c:0.00842,Th7c:0.00859,Td7c:0.01091,Ts7d:0.00842,Th7d:0.00859,Tc7d:0.01091,9h7s:0.27606,9c7s:0.26130,9d7s:0.26130,9s7h:0.19021,9c7h:0.25144,9d7h:0.25144,9s7c:0.24414,9h7c:0.27244,9d7c:0.27532,9s7d:0.24414,9h7d:0.27244,9c7d:0.27532,8h7s:0.35872,8c7s:0.32881,8d7s:0.32881,8s7h:0.15523,8c7h:0.38563,8d7h:0.38563,8s7c:0.43522,8h7c:0.34888,8d7c:0.41201,8s7d:0.43522,8h7d:0.34888,8c7d:0.41201,7h7s:0.04811,7c7s:0.01322,7d7s:0.01322,7c7h:0.76467,7d7h:0.76467,7d7c:0.76744,7s6s:0.00896,7h6h:0.57886,7c6c:0.63792,7d6d:0.63792,7s5s:0.00034,7c5c:0.06940,7d5d:0.06940,7s4s:0.01065,7h4h:0.47597,7c4c:0.48357,7d4d:0.48357,7s3s:0.03498,7h3h:0.80256,7c3c:0.88125,7d3d:0.88125,7s2s:0.00172,7h2h:0.19045,7c2c:0.21533,7d2d:0.21533,Ac6h:0.00958,Ad6h:0.00958,Ah6c:0.14727,Ad6c:0.01507,Ah6d:0.14727,Ac6d:0.01507,Kh6s:0.01523,Kc6s:0.00181,Kd6s:0.00181,Kc6h:0.06383,Kd6h:0.06383,Kh6c:0.03904,Kd6c:0.00175,Kh6d:0.03904,Kc6d:0.00175,Qh6s:0.00002,Qc6s:0.00002,Qd6s:0.00002,Qs6h:0.00002,Qc6h:0.00002,Qd6h:0.00002,Qs6c:0.00002,Qh6c:0.00002,Qd6c:0.00002,Qs6d:0.00002,Qh6d:0.00002,Qc6d:0.00002,8h6s:0.02504,8c6s:0.02528,8d6s:0.02528,8s6h:0.01026,8c6h:0.02297,8d6h:0.02297,8s6c:0.02703,8h6c:0.02683,8d6c:0.02668,8s6d:0.02703,8h6d:0.02683,8c6d:0.02668,7h6s:0.20248,7c6s:0.51158,7d6s:0.51158,7s6h:0.51072,7c6h:0.44159,7d6h:0.44159,7s6c:0.50493,7h6c:0.49359,7d6c:0.50504,7s6d:0.50493,7h6d:0.49359,7c6d:0.50504,6h6s:0.24443,6c6s:0.10354,6d6s:0.10354,6c6h:0.48878,6d6h:0.48878,6d6c:0.47965,6c5c:0.23761,6d5d:0.23761,6h4h:0.57686,6c4c:0.67641,6d4d:0.67641,6s3s:0.02100,6h3h:0.79689,6c3c:0.81447,6d3d:0.81447,6s2s:0.00008,6h2h:0.00008,6c2c:0.00008,6d2d:0.00008,Jh5s:0.00003,Jc5s:0.00003,Jd5s:0.00003,Js5c:0.00003,Jh5c:0.00003,Jd5c:0.00003,Js5d:0.00003,Jh5d:0.00003,Jc5d:0.00003,8h5s:0.00000,8c5s:0.00000,8d5s:0.00000,8s5c:0.00000,8h5c:0.00000,8d5c:0.00000,8s5d:0.00000,8h5d:0.00000,8c5d:0.00000,6h5s:0.03000,6c5s:0.03824,6d5s:0.03824,6s5c:0.02989,6h5c:0.08712,6d5c:0.19753,6s5d:0.02989,6h5d:0.08712,6c5d:0.19753,5c4c:0.15142,5d4d:0.15142,5c3c:0.01564,5d3d:0.01564,5c2c:0.27472,5d2d:0.27472,Ac4h:0.00742,Ad4h:0.00742,Ah4c:0.18256,Ah4d:0.18256,Kh4s:0.00035,Kc4s:0.00028,Kd4s:0.00028,Kc4h:0.00700,Kd4h:0.00700,Kh4c:0.00303,Kd4c:0.00004,Kh4d:0.00303,Kc4d:0.00004,Qh4s:0.00001,Qc4s:0.00001,Qd4s:0.00001,Qs4h:0.00001,Qc4h:0.00001,Qd4h:0.00001,Qs4c:0.00001,Qh4c:0.00001,Qd4c:0.00001,Qs4d:0.00001,Qh4d:0.00001,Qc4d:0.00001,Jh4s:0.00003,Jc4s:0.00003,Jd4s:0.00003,Js4h:0.00003,Jc4h:0.00003,Jd4h:0.00003,Js4c:0.00003,Jh4c:0.00003,Jd4c:0.00003,Js4d:0.00003,Jh4d:0.00003,Jc4d:0.00003,5c4s:0.09257,5d4s:0.09257,5s4h:0.01837,5c4h:0.14594,5d4h:0.14594,5s4c:0.01984,5d4c:0.03395,5s4d:0.01984,5c4d:0.03395,4h4s:0.79165,4c4s:0.98599,4d4s:0.98599,4c4h:0.58395,4d4h:0.58395,4d4c:0.90187,4s3s:0.00725,4h3h:0.07954,4c3c:0.10778,4d3d:0.10778,4s2s:0.00821,4h2h:0.16719,4c2c:0.29815,4d2d:0.29815,Ah3c:0.25875,Ah3d:0.25875,Kh3s:0.00002,Kc3s:0.00002,Kd3s:0.00002,Kc3h:0.00002,Kd3h:0.00002,Kh3c:0.00002,Kd3c:0.00002,Kh3d:0.00002,Kc3d:0.00002,Qh3s:0.00003,Qc3s:0.00003,Qd3s:0.00003,Qs3h:0.00003,Qc3h:0.00003,Qd3h:0.00003,Qs3c:0.00003,Qh3c:0.00003,Qd3c:0.00003,Qs3d:0.00003,Qh3d:0.00003,Qc3d:0.00003,3h3s:0.19145,3c3s:0.75371,3d3s:0.75371,3c3h:0.95809,3d3h:0.95809,3d3c:0.95033,3s2s:0.00302,3h2h:0.16988,3c2c:0.18026,3d2d:0.18026,Ah2s:0.00144,Kh2s:0.00001,Kc2s:0.00001,Kd2s:0.00001,Kc2h:0.00001,Kd2h:0.00001,Kh2c:0.00001,Kd2c:0.00001,Kh2d:0.00001,Kc2d:0.00001,2h2s:0.85602,2c2s:0.83773,2d2s:0.83773,2c2h:0.97391,2d2h:0.97391,2d2c:0.89256
        """

        r.clipboard_append(range_str)
        r.update()  # now it stays on the clipboard after the window is closed
        r.destroy()
        tkinter.messagebox.showinfo(title="Range export", message="range export successful, copied to clipboard.")
    else:
        tkinter.messagebox.showinfo(title="Range export", message="no range to export")

btn_copy_range = tk.Button(root, text ="Copy Range", command=copy_range_str)
btn_copy_range.place(x=200, y=650)

# run the app
root.mainloop()
