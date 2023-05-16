package com.google.gson;

import java.lang.reflect.Field;
import java.lang.reflect.GenericArrayType;
import java.lang.reflect.ParameterizedType;
import java.lang.reflect.Type;
import java.lang.reflect.TypeVariable;
import java.lang.reflect.WildcardType;

import static org.junit.Assert.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import java.util.ArrayList;
import java.util.List;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.Mock;
import org.mockito.junit.MockitoJUnitRunner;

@RunWith(MockitoJUnitRunner.class)
public class TypeInfoFactory_6576_1Test {

    @Mock
    private Field field;

    @Test
    public void getTypeInfoForArray_shouldReturnCorrectTypeInfo() {
        Type type = new String[0].getClass();
        TypeInfoArray result = TypeInfoFactory.getTypeInfoForArray(type);
        assertEquals("java.lang.String[]", result.toString());
    }

    @Test
    public void getTypeInfoForField_shouldReturnCorrectTypeInfo() {
        ParameterizedType type = mock(ParameterizedType.class);
        when(type.getRawType()).thenReturn(List.class);
        when(type.getActualTypeArguments()).thenReturn(new Type[] { String.class });

        TypeInfo result = TypeInfoFactory.getTypeInfoForField(field, type);
        assertEquals("java.util.List<java.lang.String>", result.toString());
    }

    @Test
    public void getActualType_shouldReturnCorrectType() {
        Type typeToEvaluate = new TypeToken<List<String>>() {}.getType();
        Type parentType = new TypeToken<ArrayList<String>>() {}.getType();
        Class<?> rawParentClass = ArrayList.class;

        TypeInfoFactory factory = new TypeInfoFactory();
        Type result = factory.getActualType(typeToEvaluate, parentType, rawParentClass);
        assertEquals(String.class, result);
    }

    @Test
    public void extractTypeForHierarchy_shouldReturnCorrectType() {
        TypeVariable<?> typeToEvaluate = ArrayList.class.getTypeParameters()[0];
        ParameterizedType parentType = new TypeToken<ArrayList<String>>() {}.getType();

        TypeInfoFactory factory = new TypeInfoFactory();
        Type result = factory.extractTypeForHierarchy(parentType, typeToEvaluate);
        assertEquals(String.class, result);
    }

    @Test
    public void extractRealTypes_shouldReturnCorrectTypes() {
        Type[] actualTypeArguments = new Type[] { String.class };
        Type parentType = new TypeToken<List<String>>() {}.getType();
        Class<?> rawParentClass = List.class;

        TypeInfoFactory factory = new TypeInfoFactory();
        Type[] result = factory.extractRealTypes(actualTypeArguments, parentType, rawParentClass);
        assertEquals(String.class, result[0]);
    }

    @Test
    public void getIndex_shouldReturnCorrectIndex() {
        TypeVariable<?>[] types = ArrayList.class.getTypeParameters();
        TypeVariable<?> type = types[0];

        TypeInfoFactory factory = new TypeInfoFactory();
        int result = factory.getIndex(types, type);
        assertEquals(0, result);
    }
}