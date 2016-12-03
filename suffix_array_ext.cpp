
#include <Python.h>

#include <vector>
#include <array>
#include <tuple>
#include <limits>
#include <algorithm>

template <class It, class OutIt, class KeyFunc>
void CountingSort(It first, It last, OutIt out, size_t maxKey, KeyFunc&& keyFunc) {
	using KeyType = decltype(keyFunc(*first));
	std::vector<KeyType> firstPosition(maxKey + 2);
	for (auto it = first; it != last; ++it) {
		++firstPosition[keyFunc(*it) + 1];
	}
	for (size_t i = 2; i < firstPosition.size(); ++i) {
		firstPosition[i] += firstPosition[i - 1];
	}
	for (auto it = first; it != last; ++it) {
		KeyType key = keyFunc(*it);
		*(out + firstPosition[key]) = *it;
		++firstPosition[key];
	}
}

template <class T>
std::vector<T> SuffixArrayKS(const std::vector<T>& arr, T maxElem) {
	std::vector<T> rem0, rem12;
	rem0.reserve(1 + arr.size() / 3);
	rem12.reserve(2 * arr.size() / 3);
	for (size_t i = 0; i < arr.size(); i += 3)
		rem0.push_back(i);
	for (size_t i = 1; i < arr.size(); i += 3)
		rem12.push_back(i);
	for (size_t i = 2; i < arr.size(); i += 3)
		rem12.push_back(i);

	auto getElem = [maxElem, &arr] (size_t pos) -> T {
		if (pos < arr.size())
			return arr[pos];
		return maxElem + 1;
	};

	{
		std::vector<T> tmp(rem12.size());
		for (ssize_t col = 2; col >= 0; --col) {
			CountingSort(rem12.begin(), rem12.end(), tmp.begin(), maxElem + 1, [&getElem, col] (size_t pos) -> size_t {
				return getElem(pos + col);
			});
			std::swap(rem12, tmp);
		}
	}

	using TTriple = std::array<T, 3>;
	TTriple prevTriple;
	std::vector<T> positionToRank(arr.size(), -1);
	T dollarRank;
	{
		size_t rank = 0;
		bool first = true;
		for (T pos : rem12) {
			TTriple triple{getElem(pos), getElem(pos + 1), getElem(pos + 2)};
			if (!first && triple != prevTriple) {
				++rank;
			}
			first = false;
			prevTriple = triple;
			positionToRank[pos] = rank;
		}
		dollarRank = rank + 1;

		if (dollarRank < rem12.size()) {
			std::vector<T> symbols;
			symbols.reserve(rem12.size() + 1);
			for (T i = 1; i < arr.size(); i += 3)
				symbols.push_back(positionToRank[i]);
			T dollarRankPos = symbols.size();
			symbols.push_back(dollarRank);
			for (T i = 2; i < arr.size(); i += 3)
				symbols.push_back(positionToRank[i]);
			auto rankToPos = SuffixArrayKS(symbols, dollarRank);

			for(T rank = 0; rank < rankToPos.size(); ++rank) {
				T pos = rankToPos[rank];
				T arrPos;
				if (pos < dollarRankPos)
					arrPos = 1 + pos * 3;
				else if (pos > dollarRankPos)
					arrPos = 2 + (pos - dollarRankPos - 1) * 3;
				else
					continue;
				rem12[rank] = arrPos;
				positionToRank[arrPos] = rank;
			}
			dollarRank = rem12.size();
		}
	}

	auto getRank = [dollarRank, &positionToRank] (T pos) {
		if (pos < positionToRank.size())
			return positionToRank[pos];
		return dollarRank;
	};

	{
		std::vector<T> tmp(rem0.size());
		CountingSort(rem0.begin(), rem0.end(), tmp.begin(), dollarRank, [&getRank] (T pos) {
			return getRank(pos + 1);
		});
		std::swap(rem0, tmp);
		CountingSort(rem0.begin(), rem0.end(), tmp.begin(), maxElem, [&getElem] (T pos) {
			return getElem(pos);
		});
		std::swap(rem0, tmp);
	}

	std::vector<T> result;
	result.reserve(arr.size());

	{
		size_t ind0 = 0, ind12 = 0;
		while (ind0 < rem0.size() && ind12 < rem12.size()) {
			T pos0 = rem0[ind0];
			T pos12 = rem12[ind12];
			bool isLess;
			if (pos12 % 3 == 1) {
				isLess = (
					std::make_tuple(getElem(pos0), getRank(pos0 + 1)) <=
					std::make_tuple(getElem(pos12), getRank(pos12 + 1))
				);
			} else {
				isLess = (
					std::make_tuple(getElem(pos0), getElem(pos0 + 1), getRank(pos0 + 2)) <=
					std::make_tuple(getElem(pos12), getElem(pos12 + 1), getRank(pos12 + 2))
				);
			}
			if (isLess) {
				result.push_back(rem0[ind0++]);
			} else {
				result.push_back(rem12[ind12++]);
			}
		}

		while (ind0 < rem0.size())
			result.push_back(rem0[ind0++]);

		while (ind12 < rem12.size())
			result.push_back(rem12[ind12++]);

	}

	return result;
}

class TPyErr : public std::exception {};

template <class NumT>
std::vector<NumT> PyListToVector(PyObject* pyArr) {
	std::vector<NumT> arr(PyList_Size(pyArr));
	for (size_t i = 0; i < arr.size(); ++i) {
		size_t val = PyInt_AsUnsignedLongLongMask(PyList_GET_ITEM(pyArr, i));
		if (val == -1 && PyErr_Occurred())
			throw TPyErr{};
		arr[i] = val;
	}
	return arr;
}

template <class TSeqGen>
PyObject* SequenceToPyList(size_t size, TSeqGen&& seqGen) {
	PyObject* pyResult = PyList_New(size);
	if (!pyResult)
		return nullptr;
	for (size_t i = 0; i < size; ++i) {
		PyObject* val = seqGen(i);
		if (!val) {
			Py_DECREF(pyResult);
			return nullptr;
		}
		PyList_SET_ITEM(pyResult, i, val);
	}
	return pyResult;
}

template <class T>
PyObject* py_suffix_array_ks_helper(PyObject* m, PyObject* pyArr) {
	if (!PyList_Check(pyArr)) {
		return PyErr_Format(PyExc_TypeError, "arr must be of type list");
	}

	std::vector<T> arr;
	try {
		arr = PyListToVector<T>(pyArr);
	} catch (const TPyErr&) {
		return nullptr;
	}

	T maxElem = *std::max_element(arr.begin(), arr.end());

	std::vector<T> result;
	Py_BEGIN_ALLOW_THREADS
	result = SuffixArrayKS(arr, maxElem);
	Py_END_ALLOW_THREADS

	return SequenceToPyList(result.size(), [&] (size_t pos) {
		return PyInt_FromSize_t(result[pos]);
	});
}

PyObject* py_suffix_array_ks_helper_choose(PyObject* m, PyObject* pyArr) {
	if (!PyList_Check(pyArr)) {
		return PyErr_Format(PyExc_TypeError, "arr must be of type list");
	}
	// Reserve one more position for dollar
	size_t size = PyList_Size(pyArr) + 1;
	if (size < std::numeric_limits<uint16_t>::max())
		return py_suffix_array_ks_helper<uint16_t>(m, pyArr);
	else if (size < std::numeric_limits<uint32_t>::max())
		return py_suffix_array_ks_helper<uint32_t>(m, pyArr);
	return py_suffix_array_ks_helper<uint64_t>(m, pyArr);
}

PyObject* py_bwt_pixels(PyObject* m, PyObject* pyArr) {
	if (!PyList_Check(pyArr)) {
		return PyErr_Format(PyExc_TypeError, "arr must be of type list");
	}

	std::vector<uint32_t> arr;
	try {
		arr = PyListToVector<uint32_t>(pyArr);
	} catch (const TPyErr&) {
		return nullptr;
	}

	std::vector<uint32_t> suffixArray;
	Py_BEGIN_ALLOW_THREADS
	for (size_t i = 0; i < arr.size(); ++i) {
		if (arr[i] == 255)
			arr[i] = 254;
	}
	arr.back() = 255;

	suffixArray = SuffixArrayKS(arr, 255u);
	Py_END_ALLOW_THREADS

	return SequenceToPyList(arr.size(), [&] (size_t pos) {
		return PyInt_FromSize_t(
			arr[(suffixArray[pos] + suffixArray.size() - 1) % suffixArray.size()]
		);
	});
}

static PyMethodDef py_suffix_array_ext_methods[] = {
    {"suffix_array_ks_helper",
    (PyCFunction)py_suffix_array_ks_helper_choose, METH_O,
     "suffix_array_ks_helper_choose(arr, max_elem) - Compute a suffix array."},

    {"suffix_array_ks_helper",
    (PyCFunction)py_suffix_array_ks_helper<size_t>, METH_O,
     "suffix_array_ks_helper(arr, max_elem) - Compute a suffix array."},

    {"bwt_pixels",
    (PyCFunction)py_bwt_pixels, METH_O,
     "bwt_pixels(arr) - Compute BWT transform of [0-255] values array."},


    {NULL, NULL, 0, NULL}   /* sentinel */
};

PyMODINIT_FUNC
initsuffix_array_ext(void)
{
    PyObject *m;

    m = Py_InitModule("suffix_array_ext", py_suffix_array_ext_methods);
    if (m == NULL)
        return;
    /* additional initialization can happen here */
}